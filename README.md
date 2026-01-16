# Self-Reflective Chain-of-Thought (SRCoT)

**SRCoT** is a super-lightweight, hackable **two-pass** framework for running *Retrieve → Reflect → Respond* with **local OpenAI-compatible servers** (e.g., LM Studio). It supports optional **BM25 retrieval** over local corpora and an optional **Judge & Self-Assessment** extension to close the loop with targeted re-retrieval and revision.

It’s designed for **offline / edge** setups: small dependency footprint, plain JSON I/O, and transparent “evidence-grounded” answers with inline citations.

> **Compatibility note:** This version is optimized for **munich-sim** and **munich-blackout-sim** (corpora formats + conventions).

---

## Key idea (2-pass)

SRCoT executes:

1. **Pass 1 — Retrieve + Reflect**
   - Retrieve context from one or more local corpora (BM25 + optional “recent” pinning).
   - Ask the model to produce:
     - a short **draft**
     - optional **follow-up retrieval queries** (as JSON)

2. **Pass 2 — Retrieve again + Finalize**
   - Re-retrieve using the question + (some) followups.
   - Additionally **expand the query** with mined identifiers from question + draft (e.g., `con_fuel_mix`, `#000071`).
   - Final answer must be **grounded in CONTEXT** and include **inline citation keys**.

Optional:
3. **Judge (3rd call)**
   - Produces a *claim → evidence map* and *missing facts* queries.
   - Can recommend a **Targeted-Retrieve** control action → triggers an extra retrieve + **revise pass**.

---

## Features

### Retrieval & context building
- **BM25 RAG** over one or more corpora.
- Corpus ordering for readability: **Environment → Memory → Knowledge → Experiences**.
- Optional **recency pinning**: always include the last *N* items from a corpus (useful for logs).

### Evidence discipline
- Answers are expected to include inline citation keys like:
  - `[Memory:491 #000071 ...]`
  - `[Environment:13 Material]`
- If the model returns too few citations, SRCoT triggers a **strict rewrite** pass.

### Numeric robustness (aggregation-heavy queries)
Helpful for “totals/deltas/consumption summaries” (e.g., *Materialverbrauch*):
- **Identifier mining** for query expansion (item IDs, incident tags).
- **Smarter truncation** for log-like items (keep the *tail* so newest radio/log text isn’t cut off).
- Optional: numeric conflict scan + reconcile prompt (see `PROMPT_RECONCILE` and `find_numeric_conflicts()` in code).

### Output artifacts
- Writes a machine-readable `result.json`.
- Optionally writes a human-readable `report.md` with:
  - query2 used
  - pass1 draft + followups
  - contexts for pass1 and pass2
  - final answer
  - judge output (if enabled)

---

## Installation

Requires Python 3.9+.

`pip install openai rank-bm25 numpy`

---

## Quick start

### 1) Prepare corpora

Each corpus is a JSON list of items:

```
{
  "items": [
    { "content": "Some text...", "meta": { "nummer": "1", "artikel": "log", "einsatzNr": "000071" } },
    { "content": "Another entry...", "meta": { "nummer": "2" } }
  ]
}
```

SRCoT expects:
- `content` (string): the text to retrieve
- `meta` (object): optional metadata (helps retrieval + citations)

If `meta.nummer` is missing, SRCoT auto-fills it.

You can also provide the list directly instead of wrapping it in `{ "items": ... }`.

### 2) Create a request.json

Minimal example:

```
{
  "question": "Geräte und Materialien: Welchen Gesamtmaterialverbrauch haben wir bisher?",
  "llm": {
    "base_url": "http://localhost:1234/v1",
    "model": "gpt-oss-120b",
    "temperature": 0.2,
    "max_tokens": 8192,
    "api_key": "lm-studio"
  },
  "retrieval": {
    "top_k": { "Knowledge": 15, "Memory": 10, "Experiences": 10, "Environment": 10 },
    "recent_k": { "Memory": 40, "Environment": 40, "Knowledge": 0, "Experiences": 0 },
    "per_doc_chars": 800,
    "max_followups": 5,
    "query2_max_followups": 2,
    "min_citations": 2,
    "enable_control_loop": true
  },
  "corpora": {
    "Knowledge": "knowledge.json",
    "Memory": "memory.json",
    "Experiences": "experiences.json",
    "Environment": "environment.json"
  },
  "judge": {
    "enabled": false
  }
}
```

### 3) Run

python3 srcot.py --input request.json --base_url http://localhost:1234/v1 --model gpt-oss-120b --out result.json --out_md report.md

---

## How SRCoT “grounds” answers

SRCoT formats retrieved items with citation keys like:
- `[Memory:491 #000071 ...] <content...>`
- `[Environment:13 Material] <content...>`

The final prompt explicitly instructs the model to:
- use **ONLY CONTEXT**
- output `not specified` if information is missing
- attach citations to critical statements / numeric claims

If citations are missing, SRCoT triggers `PROMPT2_FINAL_STRICT`.

---

## Configuration toggles

### Retrieval knobs
- `retrieval.top_k`: BM25 hits per corpus.
- `retrieval.recent_k`: always include latest N items per corpus (good for logs).
- `retrieval.per_doc_chars`: truncation length per retrieved item.
- `retrieval.query2_max_followups`: limit how many followups are injected into query2.

### Evidence knobs
- `retrieval.min_citations`: enforce minimum number of inline citations.

### Control loop knobs
- `judge.enabled`: enable the Judge pass.
- `retrieval.enable_control_loop`: allow Judge to trigger targeted re-retrieval and revision.

---

## Optional: enabling the Judge

Set in `request.json`:

```
"judge": {
  "enabled": true,
  "model": "gpt-oss-120b",
  "temperature": 0.0,
  "max_tokens": 8192,
  "per_doc_chars": 650,
  "top_k": { "Knowledge": 8, "Memory": 4, "Experiences": 4, "Environment": 4 }
}
```

The Judge produces:
- claims + evidence queries
- missing critical facts + queries
- contraindication/conflict queries
- a recommended control action:
  - `Targeted-Retrieve` → SRCoT retrieves more context and runs `PROMPT3_REVISE_WITH_NEW_EVIDENCE`
  - `Proceed` / `Refocus` / `Abstain`

---

## Data modeling tips (for better retrieval)

Use `meta` fields consistently to improve matching:
- `nummer`: stable id for citation
- `artikel` / `spezifikation`: “log”, “funk”, “SOP”, etc.
- `einsatzNr` (or `incidentNr`): enables incident tags like `#000071`

If your logs contain item identifiers (e.g., `con_fuel_mix`, `con_marking_tape`), keep them verbatim—SRCoT will mine and reuse them in query expansion.

---

## Typical failure modes (and mitigations)

- **Totals are wrong / brittle because evidence is distributed across many logs**  
  → increase `Memory.top_k`, raise `recent_k`, keep `per_doc_chars` high enough, ensure item IDs appear in text.

- **Model omits citations**  
  → increase `min_citations` (or keep default) to trigger strict rewrite more often.

- **Relevant log entries get truncated**  
  → log-like items use tail-truncation; increase `per_doc_chars` if needed.

- **Question is underspecified**  
  → Judge can recommend a `Refocus` action; alternatively adjust prompts to ask clarifying questions in pass1.
