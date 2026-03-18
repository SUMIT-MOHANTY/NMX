import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.slot import Slot
from app.models.user import User
from app.core.security import create_access_token
from datetime import timedelta, datetime

@pytest.mark.asyncio
async def test_reserve_slot_success(client: AsyncClient, db_session: AsyncSession):
    # Create a test user
    test_user = User(
        email="test@example.com",
        hashed_password="hashed_password"
    )
    db_session.add(test_user)
    await db_session.commit()

    # Create a test slot
    test_slot = Slot(
        name="Test Slot",
        description="Test slot for reservation",
        is_active=True
    )
    db_session.add(test_slot)
    await db_session.commit()

    # Create access token for authentication
    access_token = create_access_token(
        data={"sub": str(test_user.id)},
        expires_delta=timedelta(minutes=30)
    )

    # Prepare request payload
    reservation_date = datetime.utcnow() + timedelta(days=1)
    payload = {
        "slot_id": test_slot.id,
        "reservation_date": reservation_date.isoformat()
    }

    # Send request to reserve slot
    response = await client.post(
        "/api/v1/slots/reserve",
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # Assert response
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == test_user.id
    assert data["slot_id"] == test_slot.id
    assert data["status"] == "confirmed"

@pytest.mark.asyncio
async def test_reserve_slot_already_reserved(client: AsyncClient, db_session: AsyncSession):
    # Create a test user
    test_user = User(
        email="test2@example.com",
        hashed_password="hashed_password"
    )
    db_session.add(test_user)
    await db_session.commit()

    # Create a test slot
    test_slot = Slot(
        name="Test Slot 2",
        description="Test slot for reservation",
        is_active=True
    )
    db_session.add(test_slot)
    await db_session.commit()

    # Create access token for authentication
    access_token = create_access_token(
        data={"sub": str(test_user.id)},
        expires_delta=timedelta(minutes=30)
    )

    # Prepare request payload
    reservation_date = datetime.utcnow() + timedelta(days=1)
    payload = {
        "slot_id": test_slot.id,
        "reservation_date": reservation_date.isoformat()
    }

    # First reservation should succeed
    response1 = await client.post(
        "/api/v1/slots/reserve",
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response1.status_code == 200

    # Second reservation for same slot/date should fail
    response2 = await client.post(
        "/api/v1/slots/reserve",
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response2.status_code == 409  # Conflict
