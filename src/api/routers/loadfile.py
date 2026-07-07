from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
import uuid
from src.settings import settings
from src.api.dependencies import get_current_user
from src.database.models import User
from src.services.pdf_processor import PDFProcessorService
from src.models.document import Document
from src.utils.request_limits import validate_upload_metadata, validate_upload_size

router = APIRouter()
_processor_service: PDFProcessorService | None = None


def get_processor_service() -> PDFProcessorService:
    global _processor_service
    if _processor_service is None:
        _processor_service = PDFProcessorService()
    return _processor_service

@router.post("/upload", response_model=Document)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    validate_upload_metadata(file.filename)
    content = await file.read()
    validate_upload_size(len(content))

    # Save file
    file_id = str(uuid.uuid4())
    filename = f"{file_id}_{file.filename}"
    file_path = settings.UPLOAD_DIR / filename
    
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {e}")

    # Initialize document object
    document = Document(
        id=file_id,
        filename=file.filename,
        status="processing"
    )

    # Process in background
    background_tasks.add_task(get_processor_service().process_file, str(file_path))
    
    return document
