import sys
import json
import subprocess
from pathlib import Path
import pytest

from src.report_generator import ReportGenerator

import runpy
from pathlib import Path as _Path

def test_generate_reports_handles_internal_error(tmp_path, caplog, monkeypatch):
    gen = ReportGenerator()
    # Force an exception inside generate_reports to hit the except/log path
    monkeypatch.setattr(gen, "_create_consolidated_status", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    # Should not raise; error is logged
    gen.generate_reports(results=[], brief={}, output_dir=tmp_path)
    assert any("Failed to generate campaign_generated.json" in r.message for r in caplog.records)


def test_create_generation_report_includes_error_product():
    gen = ReportGenerator()
    results = [
        {"product_id": "p-ok", "product_name": "Ok", "status": "success", "variants": []},
        {"product_id": "p-bad", "product_name": "Bad", "status": "error", "error": "failure"},
    ]
    brief = {"campaign_id": "cid", "campaign_name": "C"}
    report = gen._create_generation_report(results, brief)
    errors = [p for p in report["products"] if p.get("status") == "error"]
    assert errors and errors[0].get("error") == "failure"


def test_report_generator_main_smoke():
    # Run the module as a script to cover the __main__ block
    # Execute from current project root (pytest sets cwd to repo root)
    result = subprocess.run([sys.executable, "-m", "src.report_generator"], capture_output=True, text=True)
    # It should exit successfully and print success message
    assert result.returncode == 0
    assert "Test campaign_generated.json generated" in (result.stdout + result.stderr)

def test_report_generator_main_inprocess(tmp_path, monkeypatch):
    # Execute the module's __main__ in-process so coverage captures it
    # Ensure cwd is repo root (assumed by tests); also ensure temp dir is clean
    temp_dir = _Path("temp")
    # Run the module as __main__
    runpy.run_module("src.report_generator", run_name="__main__")
    # Verify campaign_generated.json was written under ./temp/
    assert (temp_dir / "campaign_generated.json").exists()


