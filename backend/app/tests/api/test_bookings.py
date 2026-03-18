import asyncio
import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

from app.models.slot import Slot
from app.models.office import Office
from app.models.booking import Booking
from app.core.security import create_access_token

@pytest.fixture
async def test_office(db: AsyncSession):
    """Create a test office."""
    office = Office(
        id=uuid.uuid4(),
        name="Test Office",
        address="123 Test Street",
        city="Test City",
        country="Test Country"
    )
    db.add(office)
    await db.commit()
    return office

@pytest.fixture
async def test_slot(db: AsyncSession, test_office):
    """Create a test slot with limited capacity."""
    slot = Slot(
        id=uuid.uuid4(),
        office_id=test_office.id,
        slot_date="2024-05-15",
        slot_time="10:00:00",
        capacity=3,
        taken=0
    )
    db.add(slot)
    await db.commit()
    return slot

@pytest.fixture
def user_token():
    """Create a test user token."""
    # Create a dummy user payload
    user_data = {
        "id": uuid.uuid4(),
        "email": "test@example.com",
        "is_admin": False
    }
    return create_access_token(user_data)

@pytest.fixture
def admin_token():
    """Create a test admin token."""
    # Create a dummy admin payload
    admin_data = {
        "id": uuid.uuid4(),
        "email": "admin@example.com",
        "is_admin": True
    }
    return create_access_token(admin_data)

async def test_book_slot_success(client: AsyncClient, db: AsyncSession, test_slot, user_token):
    """Test successful booking creation."""
    # Make the booking request
    response = await client.post(
        "/api/bookings/",
        json={"slot_id": str(test_slot.id)},
        headers={"Authorization": f"Bearer {user_token}"}
    )

    # Check response
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["slot_id"] == str(test_slot.id)
    assert data["status"] == "confirmed"

    # Verify the slot's taken count was incremented
    updated_slot = await db.get(Slot, test_slot.id)
    assert updated_slot.taken == 1

async def test_book_duplicate_slot(client: AsyncClient, db: AsyncSession, test_slot, user_token):
    """Test attempting to book the same slot twice."""
    # First booking should succeed
    response1 = await client.post(
        "/api/bookings/",
        json={"slot_id": str(test_slot.id)},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response1.status_code == status.HTTP_201_CREATED

    # Second booking attempt should fail with 409 Conflict
    response2 = await client.post(
        "/api/bookings/",
        json={"slot_id": str(test_slot.id)},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response2.status_code == status.HTTP_409_CONFLICT
    assert "already have a booking" in response2.json()["detail"]

async def test_book_nonexistent_slot(client: AsyncClient, user_token):
    """Test booking a slot that doesn't exist."""
    fake_slot_id = uuid.uuid4()
    response = await client.post(
        "/api/bookings/",
        json={"slot_id": str(fake_slot_id)},
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"]

async def test_book_full_slot(client: AsyncClient, db: AsyncSession, test_slot):
    """Test booking a slot that is already at capacity."""
    # Set the slot to be at capacity
    test_slot.capacity = 1
    test_slot.taken = 1
    await db.commit()

    # Create a token for a different user
    different_user_token = create_access_token({
        "id": uuid.uuid4(),
        "email": "different@example.com",
        "is_admin": False
    })

    # Attempt to book
    response = await client.post(
        "/api/bookings/",
        json={"slot_id": str(test_slot.id)},
        headers={"Authorization": f"Bearer {different_user_token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "fully booked" in response.json()["detail"]

async def test_race_condition_handling(client: AsyncClient, db: AsyncSession, test_slot):
    """Test handling of race conditions with concurrent booking requests."""
    # Create a slot with limited capacity
    test_slot.capacity = 2
    test_slot.taken = 0
    await db.commit()

    # Create tokens for different users
    tokens = [
        create_access_token({"id": uuid.uuid4(), "email": f"user{i}@example.com", "is_admin": False})
        for i in range(5)  # 5 users will try to book simultaneously
    ]

    # Create concurrent booking requests
    async def make_booking_request(token):
        return await client.post(
            "/api/bookings/",
            json={"slot_id": str(test_slot.id)},
            headers={"Authorization": f"Bearer {token}"}
        )

    # Run all requests concurrently
    responses = await asyncio.gather(
        *[make_booking_request(token) for token in tokens],
        return_exceptions=True
    )

    # Count successful bookings
    successful_bookings = sum(1 for r in responses if not isinstance(r, Exception) and r.status_code == 201)

    # Verify only 2 bookings were created (slot capacity is 2)
    assert successful_bookings == 2

    # Check the final slot state
    updated_slot = await db.get(Slot, test_slot.id)
    assert updated_slot.taken == 2

    # Verify the rest got appropriate error responses
    error_responses = [r for r in responses if not isinstance(r, Exception) and r.status_code != 201]
    for r in error_responses:
        assert r.status_code == status.HTTP_404_NOT_FOUND
        assert "fully booked" in r.json()["detail"]

async def test_unauthenticated_request(client: AsyncClient, test_slot):
    """Test that unauthenticated requests are rejected."""
    response = await client.post(
        "/api/bookings/",
        json={"slot_id": str(test_slot.id)}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
