#!/usr/bin/env python3
"""Validate checked-in public artifacts without the private source archive."""
import json
from pathlib import Path
from export_public_case_artifacts import scan_public, sha

root = Path(__file__).resolve().parents[1] / "artifacts" / "frontiers-cases"
manifest = json.loads((root / "provenance.json").read_text(encoding="utf-8"))
assert len(manifest["public_export_sha256"]) == 5
for name, expected in manifest["public_export_sha256"].items():
    raw = (root / name).read_bytes()
    assert sha(raw) == expected, "Public file changed: " + name
    scan_public(raw.decode("utf-8"), name)
for case, info in manifest["cases"].items():
    report_name = Path(info["original_report_filename"]).stem + ".public.md"
    result_name = Path(info["original_result_filename"]).stem + ".public.json"
    report = (root / case / report_name).read_text(encoding="utf-8")
    result = json.loads((root / case / result_name).read_text(encoding="utf-8"))
    assert "contexts" not in result
    for key in ("claim_evidence_map", "missing_critical_facts_map", "contraindication_evidence"):
        assert all("evidence" not in entry for entry in result["judge"].get(key, []))
    # Public reports no longer contain the removed context/map section markers.
    final = report.split("\n## Final Answer\n", 1)[1].split("\n## Pass 1 (Reflect)\n", 1)[0].strip()
    draft = report.split("\n### Draft\n", 1)[1].split("\n### Followups\n", 1)[0].strip()
    assert final == result["final"].strip()
    assert draft == result["pass1"]["draft"].strip()
    assert "## Contexts\n" not in report
    assert "### Claim → Evidence Map\n" not in report
    assert result["public_export_notice"]["generated_text_edited"] is False
request = json.loads((root / "munich-sim-000053/request.public.json").read_text(encoding="utf-8"))
assert request["corpora"]["Knowledge"] is None
assert request["corpora"]["Experiences"] is None
assert request["corpora"]["Environment"]
assert request["corpora"]["Memory"]
print("PASS: 5 public artifact hashes; both report/result pairs; exclusions; private-path/secret scan.")
