import pytest
import uuid
from datetime import date, time, datetime, timedelta
from fastapi.testclient import TestClient
import jwt
from app.core.config import settings
from app.models.user import User
from app.models.slot import Slot
from app.models.booking import Booking
from app.models.office import Office

# Helper function to create JWT tokens for testing
def create_test_token(user_id, role="user"):
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token

@pytest.fixture
def admin_token():
    admin_id = uuid.uuid4()
    return create_test_token(admin_id, role="admin")

@pytest.fixture
def user_token():
    user_id = uuid.uuid4()
    return create_test_token(user_id, role="user")

@pytest.fixture
def test_office(db_session):
    office = Office(name="Test Office", location="Test Location")
    db_session.add(office)
    db_session.commit()
    db_session.refresh(office)
    return office

class TestAdminSlotCreation:
    def test_create_slots_admin_success(self, client, db_session, admin_token, test_office):
        # Prepare test data
        headers = {"Authorization": f"Bearer {admin_token}"}
        slot_data = [
            {
                "office_id": str(test_office.id),
                "slot_date": str(date.today() + timedelta(days=1)),
                "slot_time": "09:00:00",
                "capacity": 5
            }
        ]

        # Send request
        response = client.post("/api/admin/slots", json=slot_data, headers=headers)

        # Check response
        assert response.status_code == 201
        data = response.json()
        assert data["created"] == 1
        assert len(data["slots"]) == 1
        assert data["slots"][0]["capacity"] == 5

        # Verify slot was created in database
        slot = db_session.query(Slot).filter(
            Slot.office_id == test_office.id,
            Slot.slot_date == str(date.today() + timedelta(days=1)),
            Slot.slot_time == "09:00:00"
        ).first()
        assert slot is not None
        assert slot.capacity == 5

    def test_create_slots_non_admin_forbidden(self, client, db_session, user_token, test_office):
        # Prepare test data with regular user token
        headers = {"Authorization": f"Bearer {user_token}"}
        slot_data = [
            {
                "office_id": str(test_office.id),
                "slot_date": str(date.today() + timedelta(days=1)),
                "slot_time": "10:00:00",
                "capacity": 3
            }
        ]

        # Send request
        response = client.post("/api/admin/slots", json=slot_data, headers=headers)

        # Check response - should be forbidden
        assert response.status_code == 403
        assert response.json()["detail"] == "Admin access required"

class TestAdminSlotDeletion:
    @pytest.fixture
    def test_slot(self, db_session, test_office):
        slot = Slot(
            office_id=test_office.id,
            slot_date=date.today() + timedelta(days=2),
            slot_time=time(11, 0),
            capacity=5
        )
        db_session.add(slot)
        db_session.commit()
        db_session.refresh(slot)
        return slot

    @pytest.fixture
    def test_slot_with_booking(self, db_session, test_office, test_slot):
        # Create a test user
        user = User(
            full_name="Test User",
            email="test@example.com",
            hashed_password="hashedpassword",
            role="user"
        )
        db_session.add(user)
        db_session.commit()

        # Create a booking for the slot
        booking = Booking(
            user_id=user.id,
            slot_id=test_slot.id,
            status="confirmed"
        )
        db_session.add(booking)
        db_session.commit()

        return test_slot

    def test_delete_slot_admin_success(self, client, db_session, admin_token, test_slot):
        # Prepare request
        headers = {"Authorization": f"Bearer {admin_token}"}

        # Send request
        response = client.delete(f"/api/admin/slots/{test_slot.id}", headers=headers)

        # Check response
        assert response.status_code == 204

        # Verify slot was deleted
        slot = db_session.query(Slot).filter(Slot.id == test_slot.id).first()
        assert slot is None

    def test_delete_slot_with_bookings_fails(self, client, db_session, admin_token, test_slot_with_booking):
        # Prepare request
        headers = {"Authorization": f"Bearer {admin_token}"}

        # Send request
        response = client.delete(f"/api/admin/slots/{test_slot_with_booking.id}", headers=headers)

        # Check response - should fail because slot has bookings
        assert response.status_code == 400
        assert response.json()["detail"] == "Cannot delete slot that has existing bookings"

        # Verify slot was not deleted
        slot = db_session.query(Slot).filter(Slot.id == test_slot_with_booking.id).first()
        assert slot is not None

    def test_delete_nonexistent_slot(self, client, db_session, admin_token):
        # Prepare request with a random UUID
        headers = {"Authorization": f"Bearer {admin_token}"}
        random_id = uuid.uuid4()

        # Send request
        response = client.delete(f"/api/admin/slots/{random_id}", headers=headers)

        # Check response - should return not found
        assert response.status_code == 404
        assert response.json()["detail"] == "Slot not found"
