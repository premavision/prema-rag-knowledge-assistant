from fastapi import APIRouter, Depends

from app.api.deps import get_embedding_client, get_llm_client, get_settings, get_vector_store
from app.config.settings import Settings
from app.models.query import QueryRequest, QueryResponse
from app.services.embeddings.base import EmbeddingClient
from app.services.llm.base import LLMClient
from app.services.rag_service import RagService
from app.services.retrieval_service import RetrievalService
from app.services.vectorstore.base import VectorStore

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_knowledge_base(
    body: QueryRequest,
    settings: Settings = Depends(get_settings),
    embedding_client: EmbeddingClient = Depends(get_embedding_client),
    vector_store: VectorStore = Depends(get_vector_store),
    llm_client: LLMClient = Depends(get_llm_client),
) -> QueryResponse:
    retrieval_service = RetrievalService(
        settings=settings, embedding_client=embedding_client, vector_store=vector_store
    )
    rag_service = RagService(
        settings=settings, retrieval_service=retrieval_service, llm_client=llm_client
    )
    return await rag_service.query(question=body.question, top_k=body.top_k)
