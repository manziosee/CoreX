from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.kyc import KYCDocumentCreate, KYCDocumentResponse, KYCVerification
from app.services.kyc import KYCService
from app.models.kyc import DocumentType
from app.core.auth import get_current_active_user
from app.core.kyc_config import KYCConfig
import os
import uuid
import aiofiles

router = APIRouter()

@router.post("/documents", response_model=KYCDocumentResponse, summary="Upload KYC Document", description="Upload identity document for KYC verification")
async def upload_kyc_document(
    customer_id: str = Form(...),
    document_type: DocumentType = Form(...),
    document_number: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Validate file
    file_content = await file.read()
    file_size = len(file_content)
    
    is_valid, error_message = KYCConfig.is_file_allowed(file.filename, file_size)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    file_extension = file.filename.split(".")[-1].lower()
    
    # Save uploaded file
    file_name = f"{uuid.uuid4()}.{file_extension}"
    file_path = f"uploads/kyc/{file_name}"
    
    os.makedirs("uploads/kyc", exist_ok=True)
    
    async with aiofiles.open(file_path, "wb") as buffer:
        await buffer.write(file_content)
    
    # Create document record
    document_data = KYCDocumentCreate(
        customer_id=customer_id,
        document_type=document_type,
        document_number=document_number
    )
    
    service = KYCService(db)
    return service.upload_document(document_data, file_path)

@router.get("/customers/{customer_id}/documents", response_model=List[KYCDocumentResponse], summary="Get Customer Documents", description="Retrieve all KYC documents for a customer")
async def get_customer_documents(customer_id: str, db: Session = Depends(get_db)):
    service = KYCService(db)
    return service.get_customer_documents(customer_id)

@router.put("/documents/{document_id}/verify", response_model=KYCDocumentResponse, summary="Verify Document", description="Approve or reject a KYC document")
async def verify_document(
    document_id: str,
    verification: KYCVerification,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    # Check if user has permission to verify documents
    if current_user.role not in ["ADMIN", "AUDITOR"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    service = KYCService(db)
    document = service.verify_document(document_id, verification, str(current_user.id))
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.get("/customers/{customer_id}/status", summary="Check KYC Status", description="Check customer KYC completion status")
async def check_kyc_status(customer_id: str, db: Session = Depends(get_db)):
    from app.services.kyc_workflow import KYCWorkflowService
    workflow_service = KYCWorkflowService(db)
    return workflow_service.check_kyc_completeness(customer_id)

@router.get("/dashboard/statistics", summary="KYC Statistics", description="Get KYC processing statistics for dashboard")
async def get_kyc_statistics(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    if current_user.role not in ["ADMIN", "AUDITOR"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    from app.services.kyc_workflow import KYCWorkflowService
    workflow_service = KYCWorkflowService(db)
    return workflow_service.get_kyc_statistics()

@router.get("/requirements", summary="KYC Requirements", description="Get KYC document requirements")
async def get_kyc_requirements(customer_type: str = "individual"):
    requirements = KYCConfig.get_required_documents(customer_type)
    return {
        "customer_type": customer_type,
        "required_documents": [doc.value for doc in requirements],
        "file_constraints": {
            "max_size_mb": KYCConfig.MAX_FILE_SIZE / (1024 * 1024),
            "allowed_extensions": list(KYCConfig.ALLOWED_EXTENSIONS)
        }
    }