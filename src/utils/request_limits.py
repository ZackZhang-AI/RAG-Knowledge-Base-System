from pathlib import Path

from fastapi import HTTPException

from src.settings import settings


def validate_upload_metadata(filename: str | None) -> None:
    suffix = Path(filename or "").suffix.lower()
    if suffix not in settings.allowed_upload_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {suffix}",
        )


def validate_upload_size(
    size: int,
    max_size_bytes: int | None = None,
    max_size_mb: int | None = None,
) -> None:
    limit_bytes = max_size_bytes or settings.max_upload_size_bytes
    limit_mb = max_size_mb or settings.MAX_UPLOAD_SIZE_MB
    if size > limit_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File is larger than {limit_mb} MB.",
        )


def validate_query_text(query: str, max_length: int | None = None) -> None:
    limit = max_length or settings.MAX_QUERY_LENGTH
    if len(query.strip()) > limit:
        raise HTTPException(
            status_code=400,
            detail=f"Query is longer than {limit} characters.",
        )
