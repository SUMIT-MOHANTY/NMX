import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)

async def log_activity(
    user_id: int,
    action: str,
    resource_id: int = None,
    details: str = None
):
    """
    Logs user activity for security audit purposes.

    Args:
        user_id: The ID of the user who performed the action
        action: The type of action performed (e.g., "login", "slot_reserved")
        resource_id: ID of the resource that was acted upon (optional)
        details: Additional details about the action (optional)
    """
    try:
        db = next(get_db())

        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            resource_id=resource_id,
            details=details,
            ip_address=None,  # Would be captured in a real implementation
            timestamp=datetime.utcnow()
        )

        db.add(log_entry)
        await db.commit()

    except Exception as e:
        logger.error(f"Failed to log activity: {e}")
        # Don't raise the exception - logging failures shouldn't break the app
