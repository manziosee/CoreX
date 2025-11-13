# KYC (Know Your Customer) Feature

## Overview

The KYC feature provides comprehensive customer identity verification and document management capabilities for regulatory compliance.

## Features

### 1. Customer Onboarding
- Enhanced customer registration with additional fields
- Address, occupation, and income information collection
- Automatic KYC status initialization

### 2. Document Management
- Upload identity documents (ID, Passport, Utility Bills)
- File validation (type, size, format)
- Secure file storage with unique identifiers
- Document status tracking (Pending, Approved, Rejected)

### 3. Verification Workflow
- Role-based document verification (Admin, Auditor)
- Approval/rejection with reason tracking
- Automatic customer status updates
- Audit trail for all verification actions

### 4. Compliance Features
- Configurable document requirements
- Document expiry tracking
- Risk assessment framework
- Comprehensive audit logging

## API Endpoints

### Customer Onboarding
```
POST /customers/onboard
```
Enhanced customer creation with additional KYC fields.

### Document Upload
```
POST /kyc/documents
```
Upload KYC documents with validation.

### Document Verification
```
PUT /kyc/documents/{document_id}/verify
```
Approve or reject documents (Admin/Auditor only).

### KYC Status Check
```
GET /kyc/customers/{customer_id}/status
```
Check customer KYC completion status.

### KYC Statistics
```
GET /kyc/dashboard/statistics
```
Get KYC processing statistics for dashboard.

### Requirements
```
GET /kyc/requirements
```
Get document requirements and constraints.

## Configuration

KYC settings are configured in `app/core/kyc_config.py`:

- Document requirements by customer type
- File upload constraints (size, format)
- Document expiry periods
- Risk assessment thresholds

## Workflow

1. **Customer Registration**: Customer provides basic information
2. **Document Upload**: Customer uploads required identity documents
3. **Verification**: Compliance officer reviews and approves/rejects documents
4. **Status Update**: Customer KYC status automatically updates based on document approvals
5. **Account Activation**: Approved customers can access full banking services

## Security

- Role-based access control for verification functions
- Secure file storage with unique identifiers
- Complete audit trail for compliance
- File type and size validation

## Testing

Run KYC-specific tests:
```bash
pytest tests/test_kyc.py -v
```

## Database Schema

### KYC Documents Table
- Document metadata and file references
- Verification status and history
- Expiry date tracking

### Enhanced Customer Table
- Additional onboarding fields
- KYC status tracking
- Relationship to documents