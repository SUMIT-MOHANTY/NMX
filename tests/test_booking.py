from unittest.mock import patch, MagicMock
import uuid
import datetime
import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.endpoints.bookings import router, generate_confirmation_code
from app.models.booking import Booking
from app.models.slot import Slot
from app.schemas.booking import BookingCreate, PersonalData

# Setup test app
app = FastAPI()
app.include_router(router, prefix="/api/bookings")

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_db():
    """Mock database session"""
    db = MagicMock(spec=Session)

    # Configure the mock to return specific data
    db.query.return_value = db
    db.filter.return_value = db
    db.first.return_value = None
    db.scalar.return_value = 0

    return db

@pytest.fixture
def mock_user():
    """Mock authenticated user"""
    user = MagicMock()
    user.id = uuid.uuid4()
    return user

def test_generate_confirmation_code():
    """Test confirmation code generation"""
    code = generate_confirmation_code()
    assert len(code) == 8
    assert all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" for c in code)

def test_create_booking_success(mock_db, mock_user):
    """Test successful booking creation"""
    # Mock slot
    mock_slot = MagicMock(spec=Slot)
    mock_slot.id = uuid.uuid4()
    mock_slot.capacity = 5
    mock_slot.slot_date = datetime.date.today()
    mock_slot.slot_time = datetime.time(9, 0)
    mock_slot.office = MagicMock()
    mock_slot.office.name = "Test Office"

    # Configure mock_db to return our mock slot
    mock_db.query.return_value.filter.return_value.first.return_value = mock_slot

    # Mock the booking object created by add
    mock_booking = MagicMock(spec=Booking)
    mock_booking.id = uuid.uuid4()
    mock_booking.user_id = mock_user.id
    mock_booking.slot_id = mock_slot.id
    mock_booking.confirmation_code = "TEST1234"
    mock_booking.status = "confirmed"
    mock_booking.created_at = datetime.datetime.now()
    mock_booking.email_sent = True

    # Configure mock_db.add to set attributes on the input object
    def mock_add(booking):
        booking.id = mock_booking.id
        booking.created_at = mock_booking.created_at
        return None

    mock_db.add.side_effect = mock_add

    # Test data
    booking_data = {
        "user_id": mock_user.id,
        "slot_id": mock_slot.id,
        "personal_data": {
            "full_name": "John Doe",
            "email": "john@example.com",
            "mobile": "1234567890"
        }
    }

    # Create the booking
    with patch('app.api.endpoints.bookings.get_db', return_value=mock_db):
        with patch('app.api.endpoints.bookings.get_current_user', return_value=mock_user):
            with patch('app.api.endpoints.bookings.send_booking_confirmation', return_value=True):
                booking_in = BookingCreate(**booking_data)
                result = app.dependency_overrides[mock_db](booking_in=booking_in, current_user=mock_user)

                # Verify the booking was created
                mock_db.add.assert_called_once()
                mock_db.commit.assert_called()
                mock_db.refresh.assert_called_once()

def test_create_booking_slot_full(mock_db, mock_user):
    """Test booking creation when slot is full"""
    # Mock slot
    mock_slot = MagicMock(spec=Slot)
    mock_slot.id = uuid.uuid4()
    mock_slot.capacity = 5

    # Configure mock_db to return our mock slot
    mock_db.query.return_value.filter.return_value.first.return_value = mock_slot

    # Configure mock_db to return booking count equal to capacity
    mock_db.query.return_value.filter.return_value.scalar.return_value = 5

    # Test data
    booking_data = {
        "user_id": mock_user.id,
        "slot_id": mock_slot.id,
        "personal_data": {
            "full_name": "John Doe",
            "email": "john@example.com",
            "mobile": "1234567890"
        }
    }

    # Create the booking with expected exception
    with patch('app.api.endpoints.bookings.get_db', return_value=mock_db):
        with patch('app.api.endpoints.bookings.get_current_user', return_value=mock_user):
            with pytest.raises(Exception) as excinfo:
                booking_in = BookingCreate(**booking_data)
                app.dependency_overrides[mock_db](booking_in=booking_in, current_user=mock_user)

            assert "Slot is no longer available" in str(excinfo.value)

def test_create_booking_duplicate(mock_db, mock_user):
    """Test booking creation with duplicate booking"""
    # Mock slot
    mock_slot = MagicMock(spec=Slot)
    mock_slot.id = uuid.uuid4()
    mock_slot.capacity = 5

    # Configure mock_db to return our mock slot
    mock_db.query.return_value.filter.return_value.first.side_effect = [
        mock_slot,  # First call for slot check
        MagicMock()  # Second call for existing booking check (returns a booking)
    ]

    # Test data
    booking_data = {
        "user_id": mock_user.id,
        "slot_id": mock_slot.id,
        "personal_data": {
            "full_name": "John Doe",
            "email": "john@example.com",
            "mobile": "1234567890"
        }
    }

    # Create the booking with expected exception
    with patch('app.api.endpoints.bookings.get_db', return_value=mock_db):
        with patch('app.api.endpoints.bookings.get_current_user', return_value=mock_user):
            with pytest.raises(Exception) as excinfo:
                booking_in = BookingCreate(**booking_data)
                app.dependency_overrides[mock_db](booking_in=booking_in, current_user=mock_user)

            assert "You already have a booking for this slot" in str(excinfo.value)

def test_create_booking_integrity_error(mock_db, mock_user):
    """Test booking creation with database integrity error"""
    # Mock slot
    mock_slot = MagicMock(spec=Slot)
    mock_slot.id = uuid.uuid4()
    mock_slot.capacity = 5

    # Configure mock_db to return our mock slot
    mock_db.query.return_value.filter.return_value.first.return_value = mock_slot

    # Configure mock_db.commit to raise IntegrityError
    mock_db.commit.side_effect = Exception("IntegrityError")

    # Test data
    booking_data = {
        "user_id": mock_user.id,
        "slot_id": mock_slot.id,
        "personal_data": {
            "full_name": "John Doe",
            "email": "john@example.com",
            "mobile": "1234567890"
        }
    }

    # Create the booking with expected exception
    with patch('app.api.endpoints.bookings.get_db', return_value=mock_db):
        with patch('app.api.endpoints.bookings.get_current_user', return_value=mock_user):
            with pytest.raises(Exception):
                booking_in = BookingCreate(**booking_data)
                app.dependency_overrides[mock_db](booking_in=booking_in, current_user=mock_user)

    # Verify rollback was called
    mock_db.rollback.assert_called_once()
