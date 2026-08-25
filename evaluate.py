"""Evaluate the deterministic pipeline across all bundled synthetic cases."""
from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.db.session import reset_database
from app.main import app

ROOT = Path(__file__).resolve().parent


def run_case(client: TestClient, case_name: str) -> dict:
    folder = ROOT / "data" / "synthetic" / case_name
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    created = client.post("/applications", json=manifest["application"])
    created.raise_for_status()
    aid = created.json()["application_id"]
    for path in sorted(folder.glob("*.txt")):
        with path.open("rb") as handle:
            response = client.post(
                f"/applications/{aid}/documents",
                files={"file": (path.name, handle, "text/plain")},
            )
        response.raise_for_status()
    analyzed = client.post(f"/applications/{aid}/analyze")
    analyzed.raise_for_status()
    return client.get(f"/applications/{aid}/analysis").json()


def main() -> None:
    truth = json.loads((ROOT / "evaluation" / "ground_truth.json").read_text(encoding="utf-8"))
    case_reports: dict[str, dict] = {}
    all_passed = True

    for case_name, expected in truth.items():
        reset_database()
        with TestClient(app) as client:
            bundle = run_case(client, case_name)
        observed_anomalies = sorted(x["anomaly_type"] for x in bundle["anomalies"])
        expected_anomalies = sorted(expected.get("expected_anomalies", []))
        checks = {
            "policy": bundle["policy"]["overall_result"] == expected["expected_policy_result"],
            "recommendation": bundle["recommendation"]["status"] == expected["expected_recommendation"],
            "anomalies": all(x in observed_anomalies for x in expected_anomalies),
            "evidence": bool(bundle["recommendation"]["evidence_ids"]),
        }
        passed = all(checks.values())
        all_passed = all_passed and passed
        case_reports[case_name] = {
            "passed": passed,
            "checks": checks,
            "observed": {
                "policy": bundle["policy"]["overall_result"],
                "recommendation": bundle["recommendation"]["status"],
                "risk_score": bundle["risk"]["score"],
                "risk_grade": bundle["risk"]["risk_grade"],
                "dscr": bundle["metrics"].get("dscr"),
                "anomalies": observed_anomalies,
            },
        }

    report = {"all_passed": all_passed, "cases": case_reports}
    (ROOT / "evaluation" / "evaluation_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
