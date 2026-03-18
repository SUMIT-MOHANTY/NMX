import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.security import get_current_user
from app.schemas.gdpr import UserExportResponse, UserDeletionConfirmation
from app.services.user_service import get_user_data_export, delete_user_account
from app.core.deps import get_db

router = APIRouter()
logger = logging.getLogger("gdpr")

@router.get("/me/export", response_model=UserExportResponse, status_code=status.HTTP_200_OK)
async def export_user_data(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Export all data associated with the authenticated user

    This endpoint provides the user with a complete export of their personal data
    and booking history, as required by GDPR Article 15 (Right of access).
    """
    try:
        logger.info(f"Data export requested for user: {current_user.id}")
        user_data = await get_user_data_export(db, current_user.id)
        return user_data

    except ValueError as e:
        logger.error(f"Error exporting data for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User data not found"
        )
    except Exception as e:
        logger.error(f"Unexpected error exporting user data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving your data"
        )

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_data(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Permanently delete the authenticated user's account and all associated data

    This endpoint implements the GDPR Article 17 (Right to erasure).
    All user data will be permanently deleted, with confirmation sent by email.
    """
    try:
        logger.info(f"Account deletion requested for user: {current_user.id}")
        success = await delete_user_account(db, current_user.id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user account"
            )

        # Return 204 No Content on successful deletion
        return None

    except Exception as e:
        logger.error(f"Error deleting user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting your account"
        )
