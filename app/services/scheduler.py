from celery import Celery
from app.core.config import settings
from app.database import SessionLocal
from app.services.interest import InterestService
from app.services.loan import LoanService
from datetime import datetime

# Initialize Celery
celery_app = Celery(
    "corex_scheduler",
    broker=settings.rabbitmq_url,
    backend=settings.redis_url
)

@celery_app.task
def post_monthly_interest():
    """Scheduled task to post monthly interest"""
    db = SessionLocal()
    try:
        service = InterestService(db)
        count = service.post_monthly_interest()
        return f"Posted interest for {count} accounts"
    finally:
        db.close()

@celery_app.task
def process_standing_orders():
    """Scheduled task to process standing orders"""
    db = SessionLocal()
    try:
        from app.models.payment import StandingOrder, StandingOrderExecution, PaymentStatus
        from app.models.transaction import Transaction, TransactionType
        import uuid
        
        # Get due standing orders
        due_orders = db.query(StandingOrder).filter(
            StandingOrder.is_active == True,
            StandingOrder.next_execution_date <= datetime.utcnow()
        ).all()
        
        processed = 0
        for order in due_orders:
            try:
                # Create transaction
                transaction = Transaction(
                    transaction_id=f"SO{str(uuid.uuid4().int)[:10]}",
                    from_account_id=order.from_account_id,
                    to_account_id=order.to_account_id,
                    amount=order.amount,
                    currency=order.currency,
                    transaction_type=TransactionType.TRANSFER,
                    description=f"Standing order: {order.description}"
                )
                
                # Create execution record
                execution = StandingOrderExecution(
                    standing_order_id=order.id,
                    amount=order.amount,
                    status=PaymentStatus.COMPLETED,
                    transaction_id=transaction.id
                )
                
                # Update next execution date
                if order.frequency == "MONTHLY":
                    from dateutil.relativedelta import relativedelta
                    order.next_execution_date += relativedelta(months=1)
                elif order.frequency == "WEEKLY":
                    from datetime import timedelta
                    order.next_execution_date += timedelta(weeks=1)
                elif order.frequency == "DAILY":
                    from datetime import timedelta
                    order.next_execution_date += timedelta(days=1)
                
                db.add(transaction)
                db.add(execution)
                processed += 1
                
            except Exception as e:
                # Log error and continue
                print(f"Error processing standing order {order.id}: {e}")
                continue
        
        db.commit()
        return f"Processed {processed} standing orders"
        
    finally:
        db.close()

# Celery beat schedule
celery_app.conf.beat_schedule = {
    'post-monthly-interest': {
        'task': 'app.services.scheduler.post_monthly_interest',
        'schedule': 30.0 * 24 * 60 * 60,  # Every 30 days
    },
    'process-standing-orders': {
        'task': 'app.services.scheduler.process_standing_orders',
        'schedule': 60.0 * 60,  # Every hour
    },
}

celery_app.conf.timezone = 'UTC'