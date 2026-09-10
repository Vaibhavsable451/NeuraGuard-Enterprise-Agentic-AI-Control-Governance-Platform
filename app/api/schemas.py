from pydantic import BaseModel
from typing import Optional, Any, List, Dict


class ChatRequest(BaseModel):
    message: str
    chat_history: Optional[List[Dict[str, Any]]] = None


class RagQueryRequest(BaseModel):
    query: str
    strategy: str = "naive"
    chat_history: Optional[List[Dict[str, Any]]] = None
    image_caption: Optional[str] = None


class DocumentUploadRequest(BaseModel):
    filename: str
    text: str
    metadata: Optional[Dict[str, Any]] = None
    namespace: Optional[str] = "default"


class AgentRunRequest(BaseModel):
    query: str
    chat_history: Optional[List[Dict[str, Any]]] = None


class GovernanceCheckRequest(BaseModel):
    text: str
    source: Optional[str] = "api"


class ApprovalDecisionRequest(BaseModel):
    reviewer: str
    reason: str = ""

class EvaluationRunRequest(BaseModel):
    scope: Optional[str] = "full"
    strategy: Optional[str] = "naive"

class ApprovalCreateRequest(BaseModel):
    request_text: str
    risk_score: int
    reason: str