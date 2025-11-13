from sqlalchemy.orm import Session
from app.models.customer import Customer, KYCStatus
from app.models.kyc import KYCDocument, DocumentStatus, DocumentType
from app.models.audit import AuditLog
from typing import Dict, List
import json

class KYCWorkflowService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_kyc_requirements(self) -> Dict[str, List[str]]:
        """Define KYC requirements for different customer types"""
        return {
            "individual": [
                DocumentType.NATIONAL_ID.value,
                DocumentType.UTILITY_BILL.value
            ],
            "business": [
                DocumentType.NATIONAL_ID.value,
                DocumentType.UTILITY_BILL.value,
                DocumentType.BANK_STATEMENT.value
            ]
        }
    
    def check_kyc_completeness(self, customer_id: str) -> Dict:
        """Check if customer has completed KYC requirements"""
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return {"complete": False, "error": "Customer not found"}
        
        documents = self.db.query(KYCDocument).filter(
            KYCDocument.customer_id == customer_id,
            KYCDocument.status == DocumentStatus.APPROVED
        ).all()
        
        requirements = self.get_kyc_requirements()["individual"]  # Default to individual
        approved_types = [doc.document_type.value for doc in documents]
        
        missing_documents = [req for req in requirements if req not in approved_types]
        
        return {
            "complete": len(missing_documents) == 0,
            "approved_documents": approved_types,
            "missing_documents": missing_documents,
            "customer_status": customer.kyc_status.value
        }
    
    def auto_update_kyc_status(self, customer_id: str, user_id: str = None):
        """Automatically update customer KYC status based on document approvals"""
        completeness = self.check_kyc_completeness(customer_id)
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        
        if not customer:
            return
        
        old_status = customer.kyc_status
        
        if completeness["complete"]:
            customer.kyc_status = KYCStatus.APPROVED
        elif any(doc.status == DocumentStatus.REJECTED for doc in customer.kyc_documents):
            customer.kyc_status = KYCStatus.REJECTED
        else:
            customer.kyc_status = KYCStatus.PENDING
        
        # Log status change
        if old_status != customer.kyc_status:
            audit_log = AuditLog(
                user_id=user_id,
                action="KYC_STATUS_UPDATE",
                resource_type="Customer",
                resource_id=customer.id,
                details={
                    "old_status": old_status.value,
                    "new_status": customer.kyc_status.value,
                    "completeness_check": completeness
                }
            )
            self.db.add(audit_log)
        
        self.db.commit()
        return customer.kyc_status
    
    def get_kyc_statistics(self) -> Dict:
        """Get KYC processing statistics"""
        total_customers = self.db.query(Customer).count()
        pending_kyc = self.db.query(Customer).filter(Customer.kyc_status == KYCStatus.PENDING).count()
        approved_kyc = self.db.query(Customer).filter(Customer.kyc_status == KYCStatus.APPROVED).count()
        rejected_kyc = self.db.query(Customer).filter(Customer.kyc_status == KYCStatus.REJECTED).count()
        
        pending_documents = self.db.query(KYCDocument).filter(KYCDocument.status == DocumentStatus.PENDING).count()
        
        return {
            "total_customers": total_customers,
            "kyc_pending": pending_kyc,
            "kyc_approved": approved_kyc,
            "kyc_rejected": rejected_kyc,
            "pending_document_reviews": pending_documents,
            "completion_rate": (approved_kyc / total_customers * 100) if total_customers > 0 else 0
        }