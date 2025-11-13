"""
KYC Configuration and Business Rules
"""

from typing import Dict, List
from app.models.kyc import DocumentType

class KYCConfig:
    """KYC configuration and business rules"""
    
    # Document requirements by customer type
    DOCUMENT_REQUIREMENTS = {
        "individual": [
            DocumentType.NATIONAL_ID,
            DocumentType.UTILITY_BILL
        ],
        "business": [
            DocumentType.NATIONAL_ID,
            DocumentType.UTILITY_BILL,
            DocumentType.BANK_STATEMENT
        ]
    }
    
    # File upload constraints
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}
    
    # Document expiry periods (in days)
    DOCUMENT_EXPIRY = {
        DocumentType.NATIONAL_ID: 365 * 5,  # 5 years
        DocumentType.PASSPORT: 365 * 10,    # 10 years
        DocumentType.DRIVERS_LICENSE: 365 * 3,  # 3 years
        DocumentType.UTILITY_BILL: 90,      # 3 months
        DocumentType.BANK_STATEMENT: 90     # 3 months
    }
    
    # Risk scoring thresholds
    RISK_THRESHOLDS = {
        "low": 0.3,
        "medium": 0.7,
        "high": 1.0
    }
    
    # Auto-approval rules
    AUTO_APPROVAL_ENABLED = False
    AUTO_APPROVAL_THRESHOLD = 0.2
    
    @classmethod
    def get_required_documents(cls, customer_type: str = "individual") -> List[DocumentType]:
        """Get required documents for customer type"""
        return cls.DOCUMENT_REQUIREMENTS.get(customer_type, cls.DOCUMENT_REQUIREMENTS["individual"])
    
    @classmethod
    def is_file_allowed(cls, filename: str, file_size: int) -> tuple[bool, str]:
        """Check if file is allowed for upload"""
        if file_size > cls.MAX_FILE_SIZE:
            return False, f"File size exceeds {cls.MAX_FILE_SIZE / (1024*1024)}MB limit"
        
        extension = filename.split(".")[-1].lower()
        if extension not in cls.ALLOWED_EXTENSIONS:
            return False, f"File type not allowed. Allowed: {', '.join(cls.ALLOWED_EXTENSIONS)}"
        
        return True, "File is valid"