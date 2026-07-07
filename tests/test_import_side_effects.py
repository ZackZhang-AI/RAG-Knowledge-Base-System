import subprocess
import sys


def test_main_app_import_does_not_initialize_external_services():
    result = subprocess.run(
        [sys.executable, "-c", "from src.main import app; print(app.title)"],
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 0, result.stderr
    assert "RAG-PDF-System" in result.stdout
