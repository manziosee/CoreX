# 🔔 Notifications System

## Overview

The CoreX Banking System includes a comprehensive notifications system that automatically sends alerts to customers for various banking activities including transactions, KYC updates, loan status changes, and system alerts.

## Features

### 📱 Multi-Channel Support
- **SMS**: Transaction alerts and urgent notifications
- **Email**: KYC updates and detailed notifications  
- **In-App**: System notifications and alerts

### 🎯 Notification Types
- `TRANSACTION`: Credit/debit transaction alerts
- `KYC_UPDATE`: KYC verification status changes
- `LOAN_UPDATE`: Loan application and payment updates
- `ACCOUNT_UPDATE`: Account status changes
- `SYSTEM_ALERT`: System maintenance and security alerts

### 📋 Template System
- Customizable notification templates
- Variable substitution support
- Multi-language support (future)
- Template versioning and management

## Database Schema

### Notifications Table
```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY,
    customer_id UUID REFERENCES customers(id),
    user_id UUID REFERENCES users(id),
    notification_type notificationtype NOT NULL,
    channel notificationchannel NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    status notificationstatus DEFAULT 'PENDING',
    sent_at TIMESTAMP WITH TIME ZONE,
    read_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Notification Templates Table
```sql
CREATE TABLE notification_templates (
    id UUID PRIMARY KEY,
    template_code VARCHAR(50) UNIQUE NOT NULL,
    notification_type notificationtype NOT NULL,
    title_template VARCHAR(200) NOT NULL,
    message_template TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## API Endpoints

### Create Notification
```http
POST /notifications/
Content-Type: application/json
Authorization: Bearer <token>

{
    "customer_id": "uuid",
    "notification_type": "TRANSACTION",
    "channel": "SMS",
    "title": "Transaction Alert",
    "message": "Your account has been credited with $100"
}
```

### Get Customer Notifications
```http
GET /notifications/customer/{customer_id}?limit=50
Authorization: Bearer <token>
```

### Mark Notification as Read
```http
PUT /notifications/{notification_id}/read
Authorization: Bearer <token>
```

### Create Notification Template
```http
POST /notifications/templates
Content-Type: application/json
Authorization: Bearer <token>

{
    "template_code": "CUSTOM_ALERT",
    "notification_type": "SYSTEM_ALERT",
    "title_template": "Alert: {type}",
    "message_template": "System alert: {message} at {time}"
}
```

## Service Integration

### Transaction Notifications
Automatically triggered when transactions are processed:

```python
# In TransactionService.process_transaction()
def _send_transaction_notifications(self, transaction: Transaction):
    notification_service = NotificationService(self.db)
    
    # Notify sender
    if transaction.from_account_id:
        notification_service.send_transaction_notification(
            customer_id, amount, "debited"
        )
    
    # Notify receiver  
    if transaction.to_account_id:
        notification_service.send_transaction_notification(
            customer_id, amount, "credited"
        )
```

### KYC Notifications
Triggered when KYC status changes:

```python
# In KYCWorkflowService.auto_update_kyc_status()
def _send_kyc_notification(self, customer_id: str, status: str):
    notification_service = NotificationService(self.db)
    notification_service.send_kyc_notification(customer_id, status)
```

## Usage Examples

### Setup Default Templates
```python
from app.services.notification import NotificationService

service = NotificationService(db)
service._setup_default_templates()
```

### Send Custom Notification
```python
from app.schemas.notification import NotificationCreate
from app.models.notification import NotificationType, NotificationChannel

notification_data = NotificationCreate(
    customer_id="customer-uuid",
    notification_type=NotificationType.SYSTEM_ALERT,
    channel=NotificationChannel.EMAIL,
    title="System Maintenance",
    message="Scheduled maintenance on Sunday 2AM-4AM"
)

notification = service.create_notification(notification_data)
```

### Get Customer Notifications
```python
notifications = service.get_customer_notifications(
    customer_id="customer-uuid",
    limit=20
)

for notification in notifications:
    print(f"{notification.title}: {notification.message}")
```

## Testing

### Unit Tests
```bash
# Run notification-specific tests
make test-notifications

# Or directly with pytest
pytest tests/test_notifications_comprehensive.py -v
```

### Integration Tests
```bash
# Test integration with other services
pytest tests/test_notifications_integration.py -v
```

### Test Coverage
```bash
# Run with coverage report
pytest --cov=app.services.notification --cov-report=html
```

## Configuration

### Environment Variables
```bash
# Email configuration (future)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# SMS configuration (future)
SMS_PROVIDER=twilio
SMS_API_KEY=your-api-key
SMS_FROM_NUMBER=+1234567890
```

### Template Variables
Available variables for templates:

**Transaction Templates:**
- `{amount}`: Transaction amount
- `{type}`: Transaction type (credit/debit)
- `{time}`: Transaction timestamp
- `{account}`: Account number

**KYC Templates:**
- `{status}`: KYC status (APPROVED/REJECTED/PENDING)
- `{customer_name}`: Customer full name
- `{date}`: Status change date

## Error Handling

The notification system is designed to be resilient:

1. **Non-blocking**: Notification failures don't affect main operations
2. **Retry mechanism**: Failed notifications can be retried
3. **Fallback templates**: Default templates used if custom ones fail
4. **Graceful degradation**: System continues working without notifications

## Future Enhancements

### Phase 1
- [ ] Email delivery integration (SMTP)
- [ ] SMS delivery integration (Twilio/AWS SNS)
- [ ] Notification preferences per customer
- [ ] Delivery status tracking

### Phase 2
- [ ] Push notifications for mobile apps
- [ ] Notification scheduling and batching
- [ ] Multi-language template support
- [ ] Rich content notifications (HTML emails)

### Phase 3
- [ ] Machine learning for notification optimization
- [ ] A/B testing for notification templates
- [ ] Advanced analytics and reporting
- [ ] Integration with external notification services

## Troubleshooting

### Common Issues

**Notifications not being sent:**
1. Check if templates are set up: `service._setup_default_templates()`
2. Verify database connection
3. Check service integration in transaction/KYC services

**Template not found errors:**
1. Ensure default templates are created
2. Check template_code spelling
3. Verify template is active (`is_active = True`)

**Database errors:**
1. Run migrations: `python3 manage_db.py upgrade`
2. Check if notification tables exist
3. Verify foreign key constraints

### Debug Mode
Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Notification service will log debug information
service = NotificationService(db)
```

## Security Considerations

1. **Data Privacy**: Notification content should not include sensitive data
2. **Access Control**: Only authorized users can create/view notifications
3. **Rate Limiting**: Prevent notification spam
4. **Audit Trail**: All notifications are logged for compliance

## Performance

- **Async Processing**: Notifications sent asynchronously (future)
- **Batching**: Multiple notifications can be batched
- **Caching**: Template caching for better performance
- **Indexing**: Database indexes on customer_id and created_at