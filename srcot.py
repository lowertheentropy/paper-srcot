#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
srcot.py — v.1.3 — Super-lightweight 2-pass "Retrieve → Reflect → Respond" framework
for local OpenAI-compatible servers (LM Studio, etc.) + optional BM25 RAG
+ optional 1-step "Judge & Self Assessment" extension.

Design goals:
- 1 input JSON → 2 LLM calls (Reflect, Finalize)
- Optional 3rd LLM call: Judge (claim→evidence map, missing critical facts, conflicts, confidence, control action)
- dead simple, readable, hackable
- works for "any purpose", but supports your 4 EMS corpora out of the box:
  Knowledge / Memory / Experiences / Environment

Patch add-ons (minimal):
- GWT-ish workspace ordering: Environment → Memory → Knowledge → Experiences
- Evidence discipline: if too few inline citations, one strict rewrite pass
- Close the loop: if Judge recommends Targeted-Retrieve, run one extra targeted retrieve + revise

- Added v.1.0: Generic summary prioritization in context (summary score + sorting) so that aggregate/overview blocks (totals/diffs/overview) end up “at the top” in the prompt → reduces the model from only summing up individual logs and overlooking totals.
- Added v.1.1: Generic numeric conflict check + reconcile pass, which automatically forces a revision in case of conflicting numbers (quote both sides + name delta) → prevents silent misjudgments in case of inconsistent sources.
- Added v.1.2: Support other LLMs, improved llm output for follow-up system.
- Added v.1.3: Prompt reflection should abstain from human-asking questions. Rather follow-up the corpora.

Deps:
  pip install openai rank-bm25 numpy

Usage:
  python3 srcot.py --input request.json --base_url http://localhost:1234/v1 --model gpt-oss-120b --out result.json --out_md report.md
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from rank_bm25 import BM25Okapi

try:
    from openai import OpenAI
except Exception as e:
    raise RuntimeError("Missing dependency: openai. Install with: pip install openai") from e


# =============================================================================
# EXCHANGEABLE VARS (edit here; request.json/CLI can still override)
# =============================================================================

# LLM defaults (used if not provided in request.json)
DEFAULT_BASE_URL = "http://localhost:1234/v1"
DEFAULT_MODEL = "gpt-oss-120b"
DEFAULT_API_KEY = "lm-studio"

DEFAULT_TEMPERATURE = 0.2
DEFAULT_MAX_TOKENS = 131072

# Retrieval defaults
DEFAULT_TOP_K = {"Knowledge": 15, "Memory": 10, "Experiences": 10, "Environment": 10}
DEFAULT_RECENT_K = {"Memory": 40, "Environment": 40, "Knowledge": 0, "Experiences": 0}
DEFAULT_PER_DOC_CHARS = 800
DEFAULT_MAX_FOLLOWUPS = 5

# Keep BM25 focused: only include top-N followups into query2 (the rest are still shown to Pass2)
DEFAULT_QUERY2_MAX_FOLLOWUPS = 2

# Evidence discipline: minimum number of inline citation keys like [Knowledge:12 ...]
DEFAULT_MIN_CITATIONS = 2

# Close-the-loop controller intervention after Judge?
DEFAULT_ENABLE_CONTROL_LOOP = True

# Judge defaults (disabled by default; enable in request.json or set DEFAULT_JUDGE_ENABLED=True)
DEFAULT_JUDGE_ENABLED = False
DEFAULT_JUDGE_MODEL = "gpt-oss-120b"
DEFAULT_JUDGE_TEMPERATURE = 0.0
DEFAULT_JUDGE_MAX_TOKENS = 131072
DEFAULT_JUDGE_PER_DOC_CHARS = 650
DEFAULT_JUDGE_TOP_K = {"Knowledge": 8, "Memory": 4, "Experiences": 4, "Environment": 4}

# Conflict marker list (ACC-ish alarm). Expand freely.
CONFLICT_MARKERS = [
    "kontraindikation", "kontra", "widerspruch", "warn", "warnung", "achtung",
    "verbot", "unterlassen", "nicht anwenden", "nicht verwenden", "niemals",
    "do not", "never", "avoid",
    "interaktion", "wechselwirkung", "allerg", "cave", "risiko",
    "nur wenn", "ausnahme", "contraindication"
]

# Prompt texts (editable)
SYSTEM_DEFAULT = (
  "You are a careful assistant. "
  "You MUST follow output format rules exactly. "
  "If asked to output JSON, output ONLY valid JSON with double quotes. "
  "No markdown, no code fences, no additional text."
)

# Workspace-like corpus ordering (GWT-ish)
CORPUS_ORDER = ["Environment", "Memory", "Knowledge", "Experiences"]

PROMPT1_REFLECT = """\
Return ONLY a single JSON object. No code fences. No markdown. No extra text.

Schema (must match exactly):
{{
  "draft": "string",
  "followups": ["string", "..."]
}}

Rules:
- Use only CONTEXT as data; if missing: 'not specified'.
- Extract and include any directly available values in the draft BEFORE proposing followups.
- Followups: up to {max_followups} short, searchable questions.
- Ask a follow-up ONLY if the value is NOT present in CONTEXT.
- When creating followups, prefer queries that would retrieve missing info from the existing corpora
  (Environment for location specific information / Memory for situation; Knowledge for SOP/criteria; Experiences for prior patterns).
- DO NOT add headings like "Mögliche Follow-up-Fragen". Put them ONLY into followups[].

CONTEXT:
{context}

USER QUESTION:
{question}
"""

PROMPT1_REFLECT_RETRY = """\
Return ONLY a single JSON object. No code fences. No reasoning. No extra text.

Schema (must match exactly):
{{
  "draft": "string",
  "followups": ["string", "..."]
}}


Rules:
- Use only CONTEXT as data; if missing: 'not specified'.
- Keep followups short and searchable.
- Ask a follow-up only if the value is NOT present in CONTEXT.

CONTEXT:
{context}

USER QUESTION:
{question}
"""

PROMPT2_FINAL = """\
Finalize the answer using ONLY CONTEXT as data.

Rules:
- If something is missing, write 'not specified' (do NOT guess).
- Every critical statement should include an inline citation key copied from CONTEXT
  (example: [Knowledge:12 SOP], [Memory:?, ...], etc.).
- Output format:
  1) Direct Answer (checklist / steps) (Markdown Format)
  2) Rationale (why this is the right wording given the sources) (Markdown Format)

CONTEXT:
{context}

QUESTION:
{question}

DRAFT (from pass 1):
{draft}

FOLLOWUPS (from pass 1):
{followups}
"""

PROMPT2_FINAL_STRICT = """\
Your previous answer did not include sufficient inline citations.
Rewrite the answer using ONLY CONTEXT as data and include inline citation keys for every actionable step and every critical numeric/value statement.
If something is missing, write 'not specified' (do NOT guess).

Output format (Markdown Format):
  1) Direct Answer (checklist / steps)
  2) Current Values (e.g. explicitly list current vitals if available, else 'not specified')
  3) Rationale (why this is the right wording given the sources)

CONTEXT:
{context}

QUESTION:
{question}
"""

PROMPT3_REVISE_WITH_NEW_EVIDENCE = """\
Revise the FINAL ANSWER using ONLY the NEW CONTEXT below as additional data (do not invent).
Keep the answer locally compatible and evidence-grounded.
Every actionable step and critical numeric/value statement must carry an inline citation key copied from CONTEXT.

ORIGINAL QUESTION:
{question}

ORIGINAL FINAL ANSWER:
{final_answer}

NEW CONTEXT:
{new_context}
"""

PROMPT_JUDGE_QGEN = """\
You are the JUDGE & SELF-ASSESSMENT.

Input: QUESTION, FINAL ANSWER, CONTEXT (retrieval blocks).
Task: Break down the final answer into testable claims and derive search queries
to find evidence in the databases.

IMPORTANT:
- Rationality = overall weighting of reasons. Avoid contradictory formulations such as
  ‘rational, but overall good reasons against it’.
- Return ONLY valid JSON. No explanations outside of JSON.

Return this JSON schema:

{{
  "claims": [
    {{
      "id": "C1",
      "claim": "...",
      "critical": true,
      "query": "short BM25 search terms"
    }}
  ],
  "missing_critical_facts": [
    {{
      "id": "M1",
      "fact": "...",
      "query": "short BM25 search terms"
    }}
  ],
  "contraindication_queries": [
    "Search terms for contraindications/contradictions"
  ],
  "refocus_question": ""  // leave blank if not necessary; otherwise, ask a better, more focused question
}}

FRAGE:
{question}

FINALE ANTWORT:
{final_answer}

CONTEXT (bisher):
{context}
"""

PROMPT_RECONCILE = """\
Your answer conflicts with numeric facts in CONTEXT.

Task:
- Identify the conflicting numeric keys and values.
- Prefer the most "summary-like" sources for totals (aggregate/overview/diff style blocks),
  but ALWAYS show the supporting citations for both sides.
- If a total cannot be attributed to individual logs, state: "delta not attributable from logs".
- Do NOT invent missing evidence.

Return:
1) Direct Answer
2) Reconciliation Notes (conflicts + why you chose the total)
3) Rationale

CONTEXT:
{context}

QUESTION:
{question}

PREVIOUS FINAL:
{final}

CONFLICTS (key -> values observed):
{conflicts}
"""

# -----------------------------
# Data model
# -----------------------------

@dataclass
class Item:
    content: str
    meta: Dict[str, Any]


def load_items(path_or_inline: Any) -> List[Item]:
    """
    Accepts either:
      - a filepath (str) to JSON
      - inline list of {content, meta}
      - inline dict {"items": [...]}
    """
    if isinstance(path_or_inline, str):
        raw = json.loads(Path(path_or_inline).read_text(encoding="utf-8"))
    else:
        raw = path_or_inline

    if isinstance(raw, dict) and "items" in raw:
        raw = raw["items"]
    if not isinstance(raw, list):
        raise ValueError("Items must be a JSON list or {'items': [...]}")

    out: List[Item] = []
    for i, it in enumerate(raw):
        if not isinstance(it, dict):
            continue
        content = it.get("content")
        meta = it.get("meta") or {}
        if isinstance(content, str) and content.strip():
            if not isinstance(meta, dict):
                meta = {"meta": meta}
            out.append(Item(content=content.strip(), meta=meta))
    return out


# -----------------------------
# BM25
# -----------------------------

def _tokenize(text: str) -> List[str]:
    return re.findall(r"\w+|\S", (text or "").lower(), flags=re.UNICODE)


def _doc_text(it: Item) -> str:
    """Index content + meta fields to improve overlap."""
    parts = [it.content]
    for v in (it.meta or {}).values():
        if isinstance(v, str):
            parts.append(v)
        elif isinstance(v, (int, float)):
            parts.append(str(v))
        elif isinstance(v, list):
            parts.extend([str(x) for x in v if isinstance(x, (str, int, float))])
    return " ".join([p for p in parts if p])


class BM25Index:
    def __init__(self, items: List[Item]):
        self.items = items
        self.docs_tokens = [_tokenize(_doc_text(it)) for it in items]
        self.bm25 = BM25Okapi(self.docs_tokens)

    def retrieve(self, query: str, top_k: int) -> List[Tuple[Item, float]]:
        q = _tokenize(query)
        if not q:
            return []
        scores = self.bm25.get_scores(q)
        idx = np.argsort(scores)[::-1][:top_k]
        return [(self.items[i], float(scores[i])) for i in idx]


def _ordered_corpora(indexes: Dict[str, BM25Index]) -> List[str]:
    """Stable ordering for workspace-like readability (GWT-ish)."""
    present = set(indexes.keys())
    ordered = [c for c in CORPUS_ORDER if c in present]
    for c in indexes.keys():
        if c not in ordered:
            ordered.append(c)
    return ordered

def format_hits(hits: List[Tuple[Item, float]], corpus_name: str, per_doc_chars: int = 800) -> str:
    lines: List[str] = []
    for it, _score in hits:
        meta = (it.meta or {}) if isinstance(it.meta, dict) else {"meta": it.meta}

        nummer = meta.get("nummer", "?")
        spez = meta.get("spezifikation") or meta.get("artikel") or ""

        # Einsatz-/Incident-Bezug (für eindeutige Zuordnung)
        einsatz_nr = meta.get("einsatzNr") or meta.get("einsatznr") or meta.get("incidentNr") or meta.get("incident") or ""
        event_id = meta.get("eventId") or meta.get("event_id") or ""
        incident_tag = ""
        if einsatz_nr:
            incident_tag = f"#{einsatz_nr}"
        elif event_id:
            incident_tag = f"evt:{event_id}"

        # cite: [Memory:256 #000052 admin_injected] ...
        cite_parts = [f"{corpus_name}:{nummer}"]
        if incident_tag:
            cite_parts.append(incident_tag)
        if spez:
            cite_parts.append(str(spez).strip())

        cite = ("[" + " ".join(cite_parts) + "]").strip()

        txt = it.content or ""

        # --- NEW: smarter truncation for logs/radio ---
        artikel = str(meta.get("artikel", "") or "").lower()
        meta_str = str(meta.get("meta", "") or "").lower()
        spez_str = str(meta.get("spezifikation", "") or "").lower()

        is_log_like = (
            corpus_name.lower() in ("environment", "memory")
            and (
                "log" in artikel or "funk" in artikel or
                "log" in meta_str or "funk" in meta_str or
                "log" in spez_str or "funk" in spez_str
            )
        )

        if per_doc_chars and len(txt) > per_doc_chars:
            if is_log_like:
                # keep newest (end) so Funkverkehr nicht weggekürzt wird
                txt = _truncate_context(txt, per_doc_chars, mode="tail")  # or "head_tail"
            else:
                txt = _truncate_context(txt, per_doc_chars, mode="head")

        lines.append(f"{cite} {txt}")
    return "\n\n".join(lines)

def _truncate_context(text: str, limit: int, *, mode: str = "head") -> str:
    """
    mode:
      - "head": keep beginning
      - "tail": keep end (useful for logs where newest lines are last)
      - "head_tail": keep a bit of start + end
    """
    if not limit or len(text) <= limit:
        return text

    if mode == "tail":
        tail = text[-limit:]
        # align to newline boundary if possible (avoid cutting in middle of a line)
        nl = tail.find("\n")
        if 0 < nl < 200:
            tail = tail[nl + 1 :]
        return "…\n" + tail

    if mode == "head_tail":
        head_n = max(150, limit // 4)
        tail_n = max(150, limit - head_n - 20)
        head = text[:head_n]
        tail = text[-tail_n:]

        # neat boundaries
        head = (head.rsplit("\n", 1)[0] if "\n" in head else head).rstrip()
        nl = tail.find("\n")
        if 0 < nl < 200:
            tail = tail[nl + 1 :]
        tail = tail.lstrip()

        return f"{head}\n…\n{tail}"

    # default: "head"
    head = text[:limit]
    head = (head.rsplit(" ", 1)[0] or head).rstrip()
    return head + " …"

# -----------------------------
# LLM client
# -----------------------------

class LocalChat:
    def __init__(self, base_url: str, model: str, api_key: str = DEFAULT_API_KEY):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model

    def chat_full(self, system: str, user: str, temperature: float, max_tokens: int) -> Dict[str, Any]:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": (system or "").strip()},
                {"role": "user", "content": (user or "").strip()},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # raw dict (captures vendor extensions if present)
        if hasattr(resp, "model_dump"):
            raw = resp.model_dump()
        else:
            raw = json.loads(resp.json())

        msg = (((raw or {}).get("choices") or [{}])[0].get("message") or {})
        content = (msg.get("content") or "").strip()

        # some servers attach reasoning separately
        reasoning_field = (msg.get("reasoning") or msg.get("thoughts") or "")

        clean, reasoning_in_content = split_reasoning_from_text(content)
        reasoning_all = "\n\n".join([str(reasoning_field).strip(), reasoning_in_content]).strip()

        return {"text": clean, "reasoning": reasoning_all, "raw": raw}

    def chat(self, system: str, user: str, temperature: float, max_tokens: int) -> str:
        return (self.chat_full(system, user, temperature, max_tokens).get("text") or "").strip()


# -----------------------------
# Helpers
# -----------------------------

def _strip_code_fences(text: str) -> str:
    """
    Remove common ```json ... ``` fences (and generic ``` ... ```).
    Keeps inner content.
    """
    s = (text or "").strip()
    # ```json ... ```
    s = re.sub(r"^\s*```(?:json)?\s*", "", s, flags=re.I)
    s = re.sub(r"\s*```\s*$", "", s)
    return s.strip()


def _parse_reflect_output(text: str) -> Tuple[Dict[str, Any], bool, str]:
    """
    Parse Pass-1 output for {"draft":..., "followups":[...]}.
    Returns: (parsed, ok, mode)
      ok=True only if we successfully parsed a JSON object with required keys.
      mode: direct | extracted | fallback
    """
    s = _strip_code_fences(text)

    # 1) direct JSON
    try:
        obj = json.loads(s)
        if isinstance(obj, dict) and "draft" in obj and "followups" in obj:
            return obj, True, "direct"
    except Exception:
        pass

    # 2) extract first {...} substring and parse
    for m in re.finditer(r"\{.*?\}", s, flags=re.S):
        try:
            obj = json.loads(m.group(0))
            if isinstance(obj, dict) and "draft" in obj and "followups" in obj:
                return obj, True, "extracted"
        except Exception:
            continue

    # 3) fallback
    return {"draft": (text or "").strip(), "followups": []}, False, "fallback"

def _safe_json_parse(text: str) -> Dict[str, Any]:
    """
    Robust-ish parsing: tries direct JSON, then tries to extract the first valid {...}.
    Keep it simple, but not brittle.
    """
    text = (text or "").strip()
    try:
        return json.loads(text)
    except Exception:
        for m in re.finditer(r"\{.*?\}", text, flags=re.S):
            try:
                return json.loads(m.group(0))
            except Exception:
                continue
        return {"draft": text, "followups": []}


def _extract_json_object(text: str) -> Dict[str, Any]:
    text = (text or "").strip()
    try:
        return json.loads(text)
    except Exception:
        for m in re.finditer(r"\{.*?\}", text, flags=re.S):
            try:
                return json.loads(m.group(0))
            except Exception:
                continue
        return {}


def _merge_top_k(defaults: Dict[str, int], override: Optional[Dict[str, int]]) -> Dict[str, int]:
    out = dict(defaults)
    if isinstance(override, dict):
        for k, v in override.items():
            if v is None:
                continue
            try:
                out[k] = int(v)
            except Exception:
                pass
    return out


def _keyword_conflict_scan(text: str) -> List[str]:
    if not text:
        return []
    low = text.lower()
    out: List[str] = []
    seen = set()
    for mk in CONFLICT_MARKERS:
        mk_low = mk.lower()
        if mk_low in low and mk_low not in seen:
            out.append(mk_low)
            seen.add(mk_low)
    return out[:12]


def _count_inline_citations(text: str) -> int:
    """
    Count occurrences like [Knowledge:12 ...] or [Memory:3 ...].
    Blunt but effective evidence-discipline check.
    """
    if not text:
        return 0
    return len(re.findall(r"\[[A-Za-z]+:[^\]]+\]", text))


def _ensure_min_citations(
    chat: LocalChat,
    *,
    question: str,
    context: str,
    answer: str,
    min_citations: int,
    temperature: float,
    max_tokens: int,
) -> str:
    if _count_inline_citations(answer) >= min_citations:
        return answer
    strict = chat.chat(
        SYSTEM_DEFAULT,
        PROMPT2_FINAL_STRICT.format(context=context, question=question),
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return strict.strip() or answer


def build_context(
    indexes: Dict[str, BM25Index],
    question: str,
    top_k: Dict[str, int],
    per_doc_chars: int,
    recent_k: Optional[Dict[str, int]] = None,
) -> Tuple[str, Dict[str, str]]:

    recent_k = recent_k or {}
    per: Dict[str, str] = {}
    blocks: List[str] = []

    for corpus in _ordered_corpora(indexes):
        idx = indexes[corpus]
        k = int(top_k.get(corpus, 0))
        rk = int(recent_k.get(corpus, 0))

        hits: List[Tuple[Item, float]] = []
        if k > 0:
            hits.extend(idx.retrieve(question, k))

        # ✅ recency pinning: immer die letzten rk Items dazu
        if rk > 0:
            recent_items = idx.items[-rk:]  # assumes append-order = time-order
            # score ist egal, wir wollen sie nur drin haben
            hits.extend([(it, -1.0) for it in reversed(recent_items)])  # newest first

        hits = _dedupe_hits(hits)
        # Optional: wenn du "neueste zuerst" im Kontext willst:
        # - recency items sind schon newest-first
        # - bm25 items bleiben rank-sortiert; das ist okay

        block = format_hits(hits, corpus_name=corpus, per_doc_chars=per_doc_chars)
        per[corpus] = block
        if block.strip():
            blocks.append(f"### {corpus}\n{block}")

    return "\n\n".join(blocks).strip(), per

def _md_escape_codeblock(text: str) -> str:
    # Avoid accidental closing fences inside code blocks
    return (text or "").replace("```", "``\\`")

def split_reasoning_from_text(text: str) -> Tuple[str, str]:
    """
    Extract common local-model reasoning formats from content:
      - <think>...</think>
      - <reasoning>...</reasoning>
      - ```reasoning ... ```
      - ```thinking ... ```
    Returns: (clean_text, reasoning_text)
    """
    s = (text or "")
    reasoning_parts: List[str] = []

    # XML-ish blocks
    for tag in ["think", "reasoning"]:
        pat = re.compile(rf"<{tag}>\s*(.*?)\s*</{tag}>", flags=re.S | re.I)
        for m in pat.finditer(s):
            reasoning_parts.append(m.group(1).strip())
        s = pat.sub("", s)

    # fenced code blocks
    pat2 = re.compile(r"```(?:reasoning|thinking)\s*(.*?)```", flags=re.S | re.I)
    for m in pat2.finditer(s):
        reasoning_parts.append(m.group(1).strip())
    s = pat2.sub("", s)

    clean = s.strip()
    reasoning = "\n\n".join([p for p in reasoning_parts if p]).strip()
    return clean, reasoning

def render_markdown(res: Dict[str, Any]) -> str:
    """
    Render a human-readable Markdown report from the result dict.
    """
    meta = res.get("meta", {}) or {}
    q = meta.get("question", "") or ""
    base_url = meta.get("base_url", "") or ""
    model = meta.get("model", "") or ""
    query2 = meta.get("query2", "") or ""

    out: List[str] = []
    out.append("# SRCoT Report\n")
    out.append(f"- **Model:** `{model}`")
    out.append(f"- **Base URL:** `{base_url}`")
    out.append(f"- **Query2:** `{query2}`")
    out.append("")

    out.append("## Question")
    out.append(q if q else "_not specified_")
    out.append("")

    out.append("## Final Answer")
    out.append(res.get("final", "") or "_not specified_")
    out.append("")

    p1 = res.get("pass1", {}) or {}
    out.append("## Pass 1 (Reflect)")
    out.append("### Draft")
    out.append(p1.get("draft", "") or "_not specified_")
    out.append("")
    out.append("### Followups")
    fu = p1.get("followups", []) or []
    if isinstance(fu, list) and fu:
        out.extend([f"- {str(x)}" for x in fu if str(x).strip()])
    else:
        out.append("_none_")
    out.append("")
    out.append("### Raw (LLM output)")
    out.append("```")
    out.append(_md_escape_codeblock(p1.get("raw", "") or ""))
    out.append("```")
    out.append("")

    ctx = res.get("contexts", {}) or {}
    ctx1 = (ctx.get("pass1", {}) or {})
    ctx2 = (ctx.get("pass2", {}) or {})

    out.append("## Contexts")
    out.append("### Pass 1 Contexts")
    if isinstance(ctx1, dict) and any((isinstance(v, str) and v.strip()) for v in ctx1.values()):
        for corpus, block in ctx1.items():
            if not isinstance(block, str) or not block.strip():
                continue
            out.append(f"#### {corpus}")
            out.append("```")
            out.append(_md_escape_codeblock(block))
            out.append("```")
            out.append("")
    else:
        out.append("_none_")
        out.append("")

    out.append("### Pass 2 Contexts")
    if isinstance(ctx2, dict) and any((isinstance(v, str) and v.strip()) for v in ctx2.values()):
        for corpus, block in ctx2.items():
            if not isinstance(block, str) or not block.strip():
                continue
            out.append(f"#### {corpus}")
            out.append("```")
            out.append(_md_escape_codeblock(block))
            out.append("```")
            out.append("")
    else:
        out.append("_none_")
        out.append("")

    judge = res.get("judge")
    out.append("## Judge & Self Assessment")
    if not judge:
        out.append("_disabled / not run_")
        out.append("")
        return "\n".join(out).rstrip() + "\n"

    out.append(f"- **Confidence posture:** {judge.get('confidence_posture', '') or '_not specified_'}")
    act = judge.get("recommended_control_action", {}) or {}
    out.append(f"- **Recommended control action:** `{act.get('type','')}` — {act.get('value','')}")
    out.append("")

    out.append("### Conflict markers")
    cms = judge.get("conflict_markers", []) or []
    if isinstance(cms, list) and cms:
        out.extend([f"- `{c}`" for c in cms])
    else:
        out.append("_none_")
    out.append("")

    out.append("### Metrics")
    out.append("```json")
    out.append(json.dumps(judge.get("metrics", {}) or {}, ensure_ascii=False, indent=2))
    out.append("```")
    out.append("")

    out.append("### Claim → Evidence Map")
    cem = judge.get("claim_evidence_map", []) or []
    if isinstance(cem, list) and cem:
        for c in cem:
            if not isinstance(c, dict):
                continue
            out.append(f"#### {c.get('id','C?')} — {'CRITICAL' if c.get('critical') else 'non-critical'}")
            out.append(f"- **Claim:** {c.get('claim','')}")
            out.append(f"- **Query:** `{c.get('query','')}`")
            out.append(f"- **Has evidence:** `{bool(c.get('has_evidence'))}`")
            ev = c.get("evidence", {}) or {}
            if isinstance(ev, dict):
                for corpus, block in ev.items():
                    if not isinstance(block, str) or not block.strip():
                        continue
                    out.append(f"**{corpus}**")
                    out.append("```")
                    out.append(_md_escape_codeblock(block))
                    out.append("```")
            out.append("")
    else:
        out.append("_none_")
        out.append("")

    out.append("### Missing Critical Facts Map")
    mcf = judge.get("missing_critical_facts_map", []) or []
    if isinstance(mcf, list) and mcf:
        for m in mcf:
            if not isinstance(m, dict):
                continue
            out.append(f"#### {m.get('id','M?')}")
            out.append(f"- **Fact:** {m.get('fact','')}")
            out.append(f"- **Query:** `{m.get('query','')}`")
            out.append(f"- **Has evidence:** `{bool(m.get('has_evidence'))}`")
            ev = m.get("evidence", {}) or {}
            if isinstance(ev, dict):
                for corpus, block in ev.items():
                    if not isinstance(block, str) or not block.strip():
                        continue
                    out.append(f"**{corpus}**")
                    out.append("```")
                    out.append(_md_escape_codeblock(block))
                    out.append("```")
            out.append("")
    else:
        out.append("_none_")
        out.append("")

    out.append("### Judge raw (LLM output)")
    out.append("```")
    out.append(_md_escape_codeblock(judge.get("raw_llm", "") or ""))
    out.append("```")
    out.append("")

    return "\n".join(out).rstrip() + "\n"

def extract_key_number_pairs(text: str) -> List[Tuple[str, int]]:
    # catches patterns like "foo: 123", "foo = 123", "foo 123"
    out = []
    for m in re.finditer(r"\b([a-zA-Z_][\w\-]{2,})\b\s*(?:[:=]\s*|\s+)(\d{1,9})\b", text or ""):
        key = m.group(1).lower()
        val = int(m.group(2))
        out.append((key, val))
    return out

def find_numeric_conflicts(context: str) -> Dict[str, List[int]]:
    pairs = extract_key_number_pairs(context)
    by_key: Dict[str, set] = {}
    for k, v in pairs:
        by_key.setdefault(k, set()).add(v)
    conflicts = {k: sorted(list(vs)) for k, vs in by_key.items() if len(vs) >= 2}
    return conflicts

def mine_identifiers(text: str, limit: int = 12) -> List[str]:
    t = (text or "")
    ids = []
    ids += re.findall(r"\b[a-z]{2,}_[a-z0-9_]{2,}\b", t.lower())
    ids += re.findall(r"#\d{3,}\b", t)
    # simple de-dupe
    out = []
    seen = set()
    for x in ids:
        if x not in seen:
            out.append(x); seen.add(x)
    return out[:limit]

# -----------------------------
# Judge
# -----------------------------

def judge_and_self_assess(
    chat: LocalChat,
    indexes: Dict[str, BM25Index],
    question: str,
    final_answer: str,
    context_pass2_full: str,
    *,
    temperature: float,
    max_tokens: int,
    judge_top_k: Optional[Dict[str, int]] = None,
    per_doc_chars: int = 700,
) -> Dict[str, Any]:
    raw = chat.chat(
        SYSTEM_DEFAULT,
        PROMPT_JUDGE_QGEN.format(
            question=question,
            final_answer=final_answer,
            context=context_pass2_full,
        ),
        temperature=temperature,
        max_tokens=max_tokens,
    )
    spec = _extract_json_object(raw)

    claims = spec.get("claims") if isinstance(spec.get("claims"), list) else []
    missing = spec.get("missing_critical_facts") if isinstance(spec.get("missing_critical_facts"), list) else []
    c_queries = spec.get("contraindication_queries") if isinstance(spec.get("contraindication_queries"), list) else []
    refocus_q = spec.get("refocus_question") if isinstance(spec.get("refocus_question"), str) else ""

    topk = _merge_top_k(DEFAULT_JUDGE_TOP_K, judge_top_k)

    def retrieve_all(query: str) -> Dict[str, str]:
        blocks: Dict[str, str] = {}
        for corpus, idx in indexes.items():
            k = int(topk.get(corpus, 0))
            if k <= 0:
                continue
            hits = idx.retrieve(query, k)
            blocks[corpus] = format_hits(hits, corpus_name=corpus, per_doc_chars=per_doc_chars)
        return blocks

    # Claim → evidence map
    claim_maps: List[Dict[str, Any]] = []
    evidence_hit_count = 0
    for c in claims[:24]:
        if not isinstance(c, dict):
            continue
        cid = str(c.get("id", "")).strip() or "C?"
        claim_text = str(c.get("claim", "")).strip()
        query = str(c.get("query", "")).strip() or claim_text
        critical = bool(c.get("critical", False))

        evidence_blocks = retrieve_all(query)
        evidence_text = "\n\n".join([v for v in evidence_blocks.values() if v.strip()]).strip()
        has_evidence = bool(evidence_text)
        if has_evidence:
            evidence_hit_count += 1

        claim_maps.append({
            "id": cid,
            "claim": claim_text,
            "critical": critical,
            "query": query,
            "evidence": evidence_blocks,
            "has_evidence": has_evidence
        })

    # Missing critical facts → evidence
    missing_maps: List[Dict[str, Any]] = []
    missing_hit_count = 0
    for m in missing[:24]:
        if not isinstance(m, dict):
            continue
        mid = str(m.get("id", "")).strip() or "M?"
        fact = str(m.get("fact", "")).strip()
        query = str(m.get("query", "")).strip() or fact

        evidence_blocks = retrieve_all(query)
        evidence_text = "\n\n".join([v for v in evidence_blocks.values() if v.strip()]).strip()
        has_evidence = bool(evidence_text)
        if has_evidence:
            missing_hit_count += 1

        missing_maps.append({
            "id": mid,
            "fact": fact,
            "query": query,
            "evidence": evidence_blocks,
            "has_evidence": has_evidence
        })

    # Contraindications/conflicts
    contra_maps: List[Dict[str, Any]] = []
    contra_text_all = ""
    for q in [str(x).strip() for x in c_queries if str(x).strip()][:8]:
        ev = retrieve_all(q)
        t = "\n\n".join([v for v in ev.values() if v.strip()])
        contra_text_all += "\n" + t
        contra_maps.append({"query": q, "evidence": ev})
    conflict_markers = _keyword_conflict_scan(contra_text_all)

    # Confidence posture + one control action (deterministic)
    n_claims = max(1, len(claim_maps))
    coverage = evidence_hit_count / n_claims

    if refocus_q.strip():
        confidence = "LOW: question seems underspecified or unfocused; refocus first."
        action = {"type": "Refocus", "value": refocus_q.strip()}
    else:
        if conflict_markers:
            confidence = "LOW–MED: potential contraindications/conflicts detected; require verification."
            if missing_maps:
                action = {"type": "Targeted-Retrieve", "value": missing_maps[0]["query"]}
            else:
                action = {"type": "Ask-Human", "value": "Verify contraindications/conflicts"}
        elif coverage < 0.45 or (missing_maps and missing_hit_count == 0):
            confidence = "LOW: too few supported core claims or critical facts missing."
            qs = [mm["query"] for mm in missing_maps[:3] if mm.get("query")]
            action = {"type": "Targeted-Retrieve", "value": " | ".join(qs) if qs else question}
        elif coverage < 0.75:
            confidence = "MED: partially supported; some uncertainty remains."
            action = {"type": "Proceed", "value": "Synthesize (with caution)"}
        else:
            confidence = "HIGH: core claims mostly supported; no obvious conflicts."
            action = {"type": "Proceed", "value": "Synthesize"}

    if not context_pass2_full.strip() and not claim_maps and not missing_maps:
        confidence = "LOW: no retrievable evidence; abstain."
        action = {"type": "Abstain", "value": "No evidence in corpora"}

    return {
        "raw_llm": raw,
        "claim_evidence_map": claim_maps,
        "missing_critical_facts_map": missing_maps,
        "contraindication_evidence": contra_maps,
        "conflict_markers": conflict_markers,
        "confidence_posture": confidence,
        "recommended_control_action": action,
        "metrics": {
            "claims": len(claim_maps),
            "claims_with_evidence": evidence_hit_count,
            "coverage": coverage,
            "missing_facts": len(missing_maps),
            "missing_with_evidence": missing_hit_count,
        },
    }

def _dedupe_hits(hits: List[Tuple[Item, float]]) -> List[Tuple[Item, float]]:
    seen = set()
    out = []
    for it, sc in hits:
        key = (it.meta or {}).get("nummer") or id(it)
        if key in seen:
            continue
        seen.add(key)
        out.append((it, sc))
    return out

# -----------------------------
# Orchestration
# -----------------------------

def run_srcot(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    request.json schema (minimal):
    {
      "question": "...",
      "llm": {"base_url":"http://localhost:1234/v1", "model":"gpt-oss-120b", "temperature":0.2, "max_tokens":900},
      "retrieval": {"top_k":{"Knowledge":15,"Memory":10,"Experiences":10,"Environment":10}, "per_doc_chars":800},
      "corpora": {
        "Knowledge": "knowledge.json",
        "Memory": "memory.json",
        "Experiences": "experiences.json",
        "Environment": "environment.json"
      },
      "judge": {
        "enabled": true,
        "model": "gpt-oss-120b",
        "temperature": 0.0,
        "max_tokens": 800,
        "per_doc_chars": 650,
        "top_k": {"Knowledge":10,"Memory":4,"Experiences":4,"Environment":4}
      }
    }

    NOTE:
    - requires LocalChat.chat_full(...) to exist and return:
      { "text": "...", "reasoning": "...", "raw": {...} }
    - judge_and_self_assess(...) should (ideally) include "reasoning" + "raw_response" in its result dict.
    """
    question = request.get("question", "").strip()
    if not question:
        raise ValueError("request.question is required")

    query2 = question  # placeholder, wird nach Pass1 mit followups überschrieben

    llm_cfg = request.get("llm") or {}
    base_url = llm_cfg.get("base_url", DEFAULT_BASE_URL)
    model = llm_cfg.get("model", DEFAULT_MODEL)
    api_key = llm_cfg.get("api_key", DEFAULT_API_KEY)

    temperature = float(llm_cfg.get("temperature", DEFAULT_TEMPERATURE))
    max_tokens = int(llm_cfg.get("max_tokens", DEFAULT_MAX_TOKENS))

    ret_cfg = request.get("retrieval") or {}
    recent_k = ret_cfg.get("recent_k") or dict(DEFAULT_RECENT_K)
    top_k = ret_cfg.get("top_k") or dict(DEFAULT_TOP_K)
    per_doc_chars = int(ret_cfg.get("per_doc_chars", DEFAULT_PER_DOC_CHARS))
    max_followups = int(ret_cfg.get("max_followups", DEFAULT_MAX_FOLLOWUPS))
    query2_max_followups = int(ret_cfg.get("query2_max_followups", DEFAULT_QUERY2_MAX_FOLLOWUPS))
    min_citations = int(ret_cfg.get("min_citations", DEFAULT_MIN_CITATIONS))
    enable_control_loop = bool(ret_cfg.get("enable_control_loop", DEFAULT_ENABLE_CONTROL_LOOP))

    corpora = request.get("corpora") or {}
    if not isinstance(corpora, dict) or not corpora:
        raise ValueError("request.corpora must be a dict of corpus_name -> items (file path or inline JSON)")

    # Build indexes
    indexes: Dict[str, BM25Index] = {}
    for corpus_name, source in corpora.items():
        items = load_items(source)
        if items:
            # Make citations robust even for simple corpora (Environment/Memory)
            for i, it in enumerate(items, start=1):
                if not isinstance(it.meta, dict):
                    it.meta = {"meta": it.meta}
                it.meta.setdefault("nummer", str(i))
                it.meta.setdefault("artikel", str(it.meta.get("meta", "") or corpus_name))
            indexes[corpus_name] = BM25Index(items)

    chat = LocalChat(base_url=base_url, model=model, api_key=api_key)

    # -------------------------
    # Pass 1: retrieve + reflect
    # -------------------------

    context1, per_corpus1 = build_context(
        indexes, question, top_k=top_k, per_doc_chars=per_doc_chars, recent_k=recent_k
    )

    p1 = PROMPT1_REFLECT.format(context=context1, question=question, max_followups=max_followups)
    out1_full = chat.chat_full(SYSTEM_DEFAULT, p1, temperature=temperature, max_tokens=max_tokens)

    out1_text = (out1_full.get("text", "") or "").strip()
    pass1_reasoning = out1_full.get("reasoning", "") or ""
    pass1_raw_response = out1_full.get("raw", {}) or {}

    parsed, pass1_json_ok, pass1_parse_mode = _parse_reflect_output(out1_text)
    pass1_retries = 0

    # Retry once if Pass-1 JSON is not compliant
    if not pass1_json_ok:
        pass1_retries = 1
        p1_retry = PROMPT1_REFLECT_RETRY.format(
            context=context1,
            question=question,
        )
        out1b_full = chat.chat_full(SYSTEM_DEFAULT, p1_retry, temperature=temperature, max_tokens=max_tokens)
        out1b_text = (out1b_full.get("text", "") or "").strip()

        parsed2, ok2, mode2 = _parse_reflect_output(out1b_text)
        if ok2:
            parsed = parsed2
            pass1_json_ok = True
            pass1_parse_mode = f"retry:{mode2}"
            # keep raw history (optional but useful)
            pass1_raw_response = {"initial": pass1_raw_response, "retry": out1b_full.get("raw", {}) or {}}
            pass1_reasoning = (pass1_reasoning + "\n\n" + (out1b_full.get("reasoning", "") or "")).strip()
            out1_text = out1b_text
        else:
            pass1_parse_mode = f"fallback:{pass1_parse_mode}"

    draft = str(parsed.get("draft", "")).strip()

    followups = parsed.get("followups") or []
    if not isinstance(followups, list):
        followups = []
    followups = [str(x).strip() for x in followups if str(x).strip()][:max_followups]
    if not isinstance(followups, list):
        followups = []
    followups = [str(x).strip() for x in followups if str(x).strip()][:max_followups]

    # -----------------------------------------
    # Pass 2: re-retrieve using followups + final
    # -----------------------------------------
    followups_for_query2 = followups[:max(0, query2_max_followups)]
    query2 = " ".join([question] + followups_for_query2).strip()

    # NEW: auto identifiers
    auto_ids = mine_identifiers(question + "\n" + (draft or ""))
    query2 = " ".join([question] + followups_for_query2 + auto_ids).strip()

    context2, per_corpus2 = build_context(
        indexes, query2, top_k=top_k, per_doc_chars=per_doc_chars, recent_k=recent_k
    )

    p2 = PROMPT2_FINAL.format(
        context=context2,
        question=question,
        draft=draft or "not specified",
        followups=json.dumps(followups, ensure_ascii=False),
    )

    out2_full = chat.chat_full(SYSTEM_DEFAULT, p2, temperature=temperature, max_tokens=max_tokens)
    final = (out2_full.get("text", "") or "").strip()
    pass2_reasoning = out2_full.get("reasoning", "") or ""
    pass2_raw_response = out2_full.get("raw", {}) or {}

    final = _ensure_min_citations(
        chat,
        question=question,
        context=context2,
        answer=final,
        min_citations=min_citations,
        temperature=temperature,
        max_tokens=max_tokens,
    ).strip()

    # -------------------------
    # Optional Judge
    # -------------------------
    judge_cfg = request.get("judge") or {}
    enable_judge = bool(judge_cfg.get("enabled", DEFAULT_JUDGE_ENABLED))
    judge_res = None

    if enable_judge:
        judge_model = str(judge_cfg.get("model", DEFAULT_JUDGE_MODEL))
        judge_chat = LocalChat(base_url=base_url, model=judge_model, api_key=api_key)

        context2_full = "\n\n".join(
            [f"### {k}\n{v}" for k, v in per_corpus2.items() if isinstance(v, str) and v.strip()]
        ).strip()

        # judge_and_self_assess SHOULD use judge_chat.chat_full internally if you want reasoning there too
        judge_res = judge_and_self_assess(
            chat=judge_chat,
            indexes=indexes,
            question=question,
            final_answer=final,
            context_pass2_full=context2_full,
            temperature=float(judge_cfg.get("temperature", DEFAULT_JUDGE_TEMPERATURE)),
            max_tokens=int(judge_cfg.get("max_tokens", DEFAULT_JUDGE_MAX_TOKENS)),
            judge_top_k=judge_cfg.get("top_k"),
            per_doc_chars=int(judge_cfg.get("per_doc_chars", DEFAULT_JUDGE_PER_DOC_CHARS)),
        )

        # -------------------------
        # Close the loop (controller intervention)
        # -------------------------
        if enable_control_loop and isinstance(judge_res, dict):
            act = judge_res.get("recommended_control_action", {}) or {}
            act_type = str(act.get("type", "")).strip()
            act_value = str(act.get("value", "")).strip()

            if act_type == "Targeted-Retrieve" and act_value:
                context3, _per3 = build_context(
                    indexes, act_value, top_k=top_k, per_doc_chars=per_doc_chars, recent_k=recent_k
                )
                if context3.strip():
                    rev_full = chat.chat_full(
                        SYSTEM_DEFAULT,
                        PROMPT3_REVISE_WITH_NEW_EVIDENCE.format(
                            question=question,
                            final_answer=final,
                            new_context=context3,
                        ),
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    revised = (rev_full.get("text", "") or "").strip()
                    rev_reasoning = rev_full.get("reasoning", "") or ""
                    rev_raw_response = rev_full.get("raw", {}) or {}

                    revised = _ensure_min_citations(
                        chat,
                        question=question,
                        context=context3,
                        answer=revised,
                        min_citations=min_citations,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    ).strip()

                    if revised:
                        final = revised
                        # keep extra reasoning around (optional, but useful)
                        if rev_reasoning.strip():
                            pass2_reasoning = (pass2_reasoning + "\n\n" + rev_reasoning).strip()
                        # keep raw history (optional)
                        pass2_raw_response = {"initial": pass2_raw_response, "revised": rev_raw_response}

            elif act_type == "Abstain":
                final = (
                    "Nicht ausreichend belegbar mit den aktuell verfügbaren lokalen Quellen. "
                    "Bitte gezielt nach relevanten SOP-/Leitlinien-Abschnitten suchen oder ärztlich rücksprechen.\n"
                    f"(Controller: {act_type} — {act_value or 'not specified'})"
                )

                conflicts = find_numeric_conflicts(context2)
                if conflicts:
                    rev = chat.chat(
                        SYSTEM_DEFAULT,
                        PROMPT_RECONCILE.format(
                            context=context2,
                            question=question,
                            final=final,
                            conflicts=json.dumps(conflicts, ensure_ascii=False),
                        ),
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    final = rev.strip() or final

    return {
        "final": final,
        "pass1": {
            "raw": out1_text,  # text-only after split
            "draft": draft,
            "followups": followups,
            "reasoning": pass1_reasoning,
            "raw_response": pass1_raw_response,
        },
        "pass2": {
            "reasoning": pass2_reasoning,
            "raw_response": pass2_raw_response,
        },
        "contexts": {"pass1": per_corpus1, "pass2": per_corpus2},
        "judge": judge_res,
        "meta": {
            "model": model,
            "base_url": base_url,
            "query2": query2,
            "question": question,
            "pass1_json_ok": bool(pass1_json_ok),
            "pass1_retries": int(pass1_retries),
            "pass1_followups_n": int(len(followups)),
            "pass1_parse_mode": str(pass1_parse_mode),
        },
    }


# -----------------------------
# CLI
# -----------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to request.json")
    ap.add_argument("--base_url", default="", help="Override base_url")
    ap.add_argument("--model", default="", help="Override model")
    ap.add_argument("--out", default="", help="Optional output JSON path")
    ap.add_argument("--out_md", default="", help="Optional output Markdown path (formatted report)")
    args = ap.parse_args()

    req = json.loads(Path(args.input).read_text(encoding="utf-8"))
    if args.base_url:
        req.setdefault("llm", {})["base_url"] = args.base_url
    if args.model:
        req.setdefault("llm", {})["model"] = args.model

    res = run_srcot(req)

    # JSON output (existing behavior)
    txt = json.dumps(res, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(txt, encoding="utf-8")
    else:
        print(txt)

    # Optional Markdown output
    if args.out_md:
        md = render_markdown(res)
        Path(args.out_md).write_text(md, encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())