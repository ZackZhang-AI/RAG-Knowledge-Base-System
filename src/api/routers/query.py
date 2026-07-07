from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from src.api.dependencies import get_current_user
from src.database.models import User
from src.services.rag_service import RAGService
from src.utils.request_limits import validate_query_text

router = APIRouter()
_rag_service: RAGService | None = None


def get_rag_service() -> RAGService:
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

class QueryResponse(BaseModel):
    query: str
    answer: str
    source_documents: List[Dict[str, Any]]

@router.post("/chat", response_model=QueryResponse)
async def chat(
    request: QueryRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        validate_query_text(request.query)
        result = get_rag_service().query(request.query, request.top_k)
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
