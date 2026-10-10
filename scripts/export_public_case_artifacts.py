#!/usr/bin/env python3
"""Export reviewed case artifacts, preserving model text and excluding corpora."""
import argparse
import copy
import hashlib
import json
import re
from pathlib import Path

EXPECTED = {
    "ems/report_srcot_run_2.md": "f53c385220f06e91d833566cb5e200148dcea74a0fabad2d5a82013526be990f",
    "ems/result_srcot_run_3.json": "cfa49a1ae04a85f86a0eacd7da76e186e3d9222faf2ae82b7e82adbdda7bf6d8",
    "munich/report.md": "aaab24121b8bc463f201d4c212506fd6a78cf775bff1119adacb957b8976e20a",
    "munich/result.json": "e6c7b8bf20c15e012b70244bc62e488cddad08e05f1d79410e6d6ba061b64b7b",
    "munich/request.json": "7363791d7d0f29abb22c24c3de4e8519dfb1b83ff4d8ba56c06dc99243dc38eb",
}
PREAMBLE = (
    "> Public research-artifact export; not medical or operational guidance.\n"
    "> This is a synthetic scenario. Generated text below is reproduced without correction.\n"
    "> Retrieved contexts and evidence payloads are intentionally omitted; see the parent README.\n\n"
)
OMISSION = (
    "\n\n> PUBLIC EXPORT OMISSION: retrieved context/evidence passages are not "
    "redistributed pending source-provenance and licensing review.\n\n"
)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def read_verified(path, key):
    raw = path.read_bytes()
    if sha(raw) != EXPECTED[key]:
        raise ValueError("Source differs from the reviewed snapshot: " + key)
    return raw.decode("utf-8")

def split_report(text):
    contexts = text.index("\n## Contexts\n")
    judge = text.index("\n## Judge & Self Assessment\n", contexts)
    maps = text.index("\n### Claim → Evidence Map\n", judge)
    raw_judge = text.index("\n### Judge raw (LLM output)\n", maps)
    return [text[:contexts], text[judge:maps], text[raw_judge:]]

def report_export(text):
    parts = split_report(text)
    exported = PREAMBLE + OMISSION.join(parts)
    assert all(part in exported for part in parts)
    return exported

def result_export(original):
    result = copy.deepcopy(original)
    del result["contexts"]
    for key in ("claim_evidence_map", "missing_critical_facts_map", "contraindication_evidence"):
        for entry in result["judge"].get(key, []):
            entry.pop("evidence", None)
    result["public_export_notice"] = {
        "type": "partial_saved_artifact_not_complete_reproduction_bundle",
        "excluded": ["contexts", "judge.*[].evidence"],
        "reason": "Retrieved source passages not redistributed pending provenance and licensing review.",
        "generated_text_edited": False,
        "metrics_warning": "Stored has_evidence/coverage values reflect retrieval heuristics, not verified entailment or correctness.",
    }
    assert result["final"] == original["final"]
    assert result["pass1"] == original["pass1"]
    assert result["judge"]["raw_llm"] == original["judge"]["raw_llm"]
    return result

def consistency(report, result):
    final = report.split("\n## Final Answer\n", 1)[1].split("\n## Pass 1 (Reflect)\n", 1)[0].strip()
    draft = report.split("\n### Draft\n", 1)[1].split("\n### Followups\n", 1)[0].strip()
    summary = split_report(report)[1]
    fence = chr(96) * 3
    metrics = json.loads(summary.split("\n### Metrics\n", 1)[1].split(fence + "json\n", 1)[1].split("\n" + fence, 1)[0])
    comparisons = {
        "final_text_matches_after_trimming_outer_whitespace": final == result["final"].strip(),
        "draft_text_matches_after_trimming_outer_whitespace": draft == result["pass1"]["draft"].strip(),
        "judge_metrics_match": metrics == result["judge"]["metrics"],
    }
    if not all(comparisons.values()):
        raise ValueError("Report and selected result are not a verified pair: " + str(comparisons))
    return comparisons

def encode_json(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2) + "\n"

def scan_public(text, label):
    patterns = {
        "private_absolute_path": r"/(?:Users|home)/[^\s\"<>]+",
        "private_key": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
        "github_token": r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b",
        "api_secret": r"\bsk-[A-Za-z0-9_-]{20,}\b",
    }
    for category, pattern in patterns.items():
        if re.search(pattern, text):
            raise ValueError(category + " detected in " + label + "; refusing export")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ems-dir", type=Path, required=True)
    parser.add_argument("--munich-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    specs = [
        ("ems-report-2", args.ems_dir, "report_srcot_run_2.md", "result_srcot_run_3.json", "ems"),
        ("munich-sim-000053", args.munich_dir, "report.md", "result.json", "munich"),
    ]
    manifest = {
        "schema_version": 1,
        "export_date": "2026-10-10",
        "all_case_scenarios_synthetic": True,
        "historical_code_revision_not_established": True,
        "full_retrieved_corpora_not_redistributed": True,
        "cases": {},
    }
    outputs = {}
    for case, source_dir, report_name, result_name, key in specs:
        report = read_verified(source_dir / report_name, key + "/" + report_name)
        result = json.loads(read_verified(source_dir / result_name, key + "/" + result_name))
        outputs[case + "/" + Path(report_name).stem + ".public.md"] = report_export(report)
        outputs[case + "/" + Path(result_name).stem + ".public.json"] = encode_json(result_export(result))
        manifest["cases"][case] = {
            "original_report_filename": report_name,
            "original_report_sha256": EXPECTED[key + "/" + report_name],
            "original_result_filename": result_name,
            "original_result_sha256": EXPECTED[key + "/" + result_name],
            "report_result_consistency": consistency(report, result),
            "model_identifier_in_saved_result": result["meta"]["model"],
        }
    request = json.loads(read_verified(args.munich_dir / "request.json", "munich/request.json"))
    request["corpora"]["Knowledge"] = None
    request["corpora"]["Experiences"] = None
    request["public_export_exclusions"] = {
        "corpora.Knowledge": "Local corpus path removed; referenced corpus not redistributed.",
        "corpora.Experiences": "Local corpus path removed; referenced corpus not redistributed.",
        "execution": "This partial historical request is not directly runnable without the omitted corpora.",
    }
    outputs["munich-sim-000053/request.public.json"] = encode_json(request)
    manifest["cases"]["munich-sim-000053"]["original_request_sha256"] = EXPECTED["munich/request.json"]
    manifest["cases"]["munich-sim-000053"]["run_id"] = "srcot_1768397359157_c7f6a1"
    manifest["cases"]["ems-report-2"]["filename_pairing_note"] = (
        "report_srcot_run_2.md matches result_srcot_run_3.json by content. "
        "The numeric filename suffixes are crossed; result_srcot_run_2.json is a different saved output. "
        "Original filename stems are retained in these public exports."
    )
    manifest["cases"]["ems-report-2"]["request_limitation"] = (
        "The available local request.json names gpt-oss-20b, whereas the saved report "
        "and its matching result name gpt-oss-120b. It is not exported as the original run request."
    )
    for relative, text in outputs.items():
        scan_public(text, relative)
    manifest["public_export_sha256"] = {name: sha(text.encode("utf-8")) for name, text in outputs.items()}
    outputs["provenance.json"] = encode_json(manifest)
    for relative, text in outputs.items():
        target = args.output_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    print(encode_json({case: item["report_result_consistency"] for case, item in manifest["cases"].items()}))

if __name__ == "__main__":
    main()
