import pytest
from fastapi import HTTPException, status

from src.api.routers import auth
from src.settings import Settings


def test_settings_parse_cors_upload_extensions_and_size():
    settings = Settings(
        BACKEND_CORS_ORIGINS="https://demo.example.com, http://localhost:5173",
        ALLOWED_UPLOAD_EXTENSIONS=".pdf,.txt,.md,.docx",
        MAX_UPLOAD_SIZE_MB=10,
    )

    assert settings.cors_origins == [
        "https://demo.example.com",
        "http://localhost:5173",
    ]
    assert settings.allowed_upload_extensions == {".pdf", ".txt", ".md", ".docx"}
    assert settings.max_upload_size_bytes == 10 * 1024 * 1024


def test_register_rejects_when_public_registration_disabled():
    original = auth.settings.ALLOW_REGISTRATION
    auth.settings.ALLOW_REGISTRATION = False
    try:
        with pytest.raises(HTTPException) as exc:
            auth.register(
                auth.UserCreate(
                    username="demo",
                    email="demo@example.com",
                    password="change-me",
                ),
                db=None,
            )
    finally:
        auth.settings.ALLOW_REGISTRATION = original

    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc.value.detail == "Public registration is disabled for this demo."


def test_upload_validation_accepts_configured_extensions():
    from src.utils.request_limits import validate_upload_metadata

    validate_upload_metadata("guide.pdf")
    validate_upload_metadata("notes.MD")


def test_upload_validation_rejects_unsupported_extensions():
    from src.utils.request_limits import validate_upload_metadata

    with pytest.raises(HTTPException) as exc:
        validate_upload_metadata("archive.exe")

    assert exc.value.status_code == 400
    assert "Unsupported file type" in exc.value.detail


def test_upload_validation_rejects_files_larger_than_limit():
    from src.utils.request_limits import validate_upload_size

    limit = Settings(MAX_UPLOAD_SIZE_MB=1).max_upload_size_bytes

    with pytest.raises(HTTPException) as exc:
        validate_upload_size(limit + 1, max_size_bytes=limit, max_size_mb=1)

    assert exc.value.status_code == 413
    assert exc.value.detail == "File is larger than 1 MB."


def test_query_validation_rejects_overly_long_queries():
    from src.utils.request_limits import validate_query_text

    with pytest.raises(HTTPException) as exc:
        validate_query_text("x" * 1001, max_length=1000)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Query is longer than 1000 characters."
