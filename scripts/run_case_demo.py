"""Run any bundled synthetic case end-to-end without starting HTTP servers."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient
from app.db.session import reset_database
from app.main import app


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case", nargs="?", default="strong_case", help="Folder name under data/synthetic")
    args = parser.parse_args()

    folder = ROOT / "data" / "synthetic" / args.case
    manifest_path = folder / "manifest.json"
    if not manifest_path.exists():
        available = sorted(x.name for x in (ROOT / "data" / "synthetic").iterdir() if x.is_dir())
        raise SystemExit(f"Unknown case {args.case!r}. Available: {', '.join(available)}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    reset_database()
    with TestClient(app) as client:
        created = client.post("/applications", json=manifest["application"])
        created.raise_for_status()
        application_id = created.json()["application_id"]
        for path in sorted(folder.glob("*.txt")):
            with path.open("rb") as handle:
                response = client.post(
                    f"/applications/{application_id}/documents",
                    files={"file": (path.name, handle, "text/plain")},
                )
            response.raise_for_status()
        analyzed = client.post(f"/applications/{application_id}/analyze")
        analyzed.raise_for_status()
        bundle = client.get(f"/applications/{application_id}/analysis").json()

    print("Case:", args.case)
    print("Application:", application_id)
    print("Expected behavior:", manifest.get("expected_behavior"))
    print("Recommendation:", bundle["recommendation"]["status"])
    print("Policy:", bundle["policy"]["overall_result"])
    print("Risk:", bundle["risk"]["score"], bundle["risk"]["risk_grade"])
    print("DSCR:", bundle["metrics"].get("dscr"))
    print("Anomalies:", [x["anomaly_type"] for x in bundle["anomalies"]])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
