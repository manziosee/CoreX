from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.kyc import DocumentType, DocumentStatus

class KYCDocumentBase(BaseModel):
    document_type: DocumentType
    document_number: Optional[str] = None

class KYCDocumentCreate(KYCDocumentBase):
    customer_id: str

class KYCDocumentResponse(KYCDocumentBase):
    id: str
    customer_id: str
    file_path: Optional[str] = None
    status: DocumentStatus
    verified_by: Optional[str] = None
    rejection_reason: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class KYCVerification(BaseModel):
    status: DocumentStatus
    rejection_reason: Optional[str] = None