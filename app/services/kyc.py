from sqlalchemy.orm import Session
from app.models.kyc import KYCDocument, DocumentStatus
from app.models.customer import Customer, KYCStatus
from app.schemas.kyc import KYCDocumentCreate, KYCVerification
from typing import List, Optional
import uuid

class KYCService:
    def __init__(self, db: Session):
        self.db = db
    
    def upload_document(self, document_data: KYCDocumentCreate, file_path: str) -> KYCDocument:
        document = KYCDocument(
            **document_data.dict(),
            file_path=file_path
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document
    
    def get_customer_documents(self, customer_id: str) -> List[KYCDocument]:
        return self.db.query(KYCDocument).filter(KYCDocument.customer_id == customer_id).all()
    
    def verify_document(self, document_id: str, verification: KYCVerification, verifier_id: str) -> Optional[KYCDocument]:
        document = self.db.query(KYCDocument).filter(KYCDocument.id == document_id).first()
        if not document:
            return None
        
        document.status = verification.status
        document.verified_by = verifier_id
        if verification.rejection_reason:
            document.rejection_reason = verification.rejection_reason
        
        self.db.commit()
        
        # Update customer KYC status based on document verification
        from app.services.kyc_workflow import KYCWorkflowService
        workflow_service = KYCWorkflowService(self.db)
        workflow_service.auto_update_kyc_status(document.customer_id, verifier_id)
        
        self.db.refresh(document)
        return document
    
    def _update_customer_kyc_status(self, customer_id: str):
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return
        
        documents = self.get_customer_documents(customer_id)
        
        # Check if we have required documents
        required_docs = ["NATIONAL_ID", "UTILITY_BILL"]
        approved_doc_types = [doc.document_type for doc in documents if doc.status == DocumentStatus.APPROVED]
        
        if all(doc_type in [doc.value for doc in approved_doc_types] for doc_type in required_docs):
            customer.kyc_status = KYCStatus.APPROVED
        elif any(doc.status == DocumentStatus.REJECTED for doc in documents):
            customer.kyc_status = KYCStatus.REJECTED
        else:
            customer.kyc_status = KYCStatus.PENDING
        
        self.db.commit()