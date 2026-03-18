from datetime import date, time
import pytest
import uuid
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.models.office import Office
from app.models.slot import Slot

@pytest.fixture
def test_office(db: Session):
    """Create a test office."""
    office = Office(
        id=uuid.uuid4(),
        name="Test Passport Office",
        address="123 Main St",
        city="Test City",
        postal_code="12345",
        country="Test Country"
    )
    db.add(office)
    db.commit()
    return office

@pytest.fixture
def test_slots(db: Session, test_office):
    """Create test slots with various capacities and occupancy."""
    slots = [
        # Available slot (5 capacity, 2 taken)
        Slot(
            id=uuid.uuid4(),
            office_id=test_office.id,
            slot_date=date(2023, 10, 15),
            slot_time=time(9, 0),
            capacity=5,
            taken=2
        ),
        # Fully booked slot (3 capacity, 3 taken)
        Slot(
            id=uuid.uuid4(),
            office_id=test_office.id,
            slot_date=date(2023, 10, 15),
            slot_time=time(10, 0),
            capacity=3,
            taken=3
        ),
        # Available slot in different city
        Slot(
            id=uuid.uuid4(),
            office_id=uuid.uuid4(),  # Different office
            slot_date=date(2023, 10, 15),
            slot_time=time(11, 0),
            capacity=4,
            taken=1
        ),
        # Available slot on different date
        Slot(
            id=uuid.uuid4(),
            office_id=test_office.id,
            slot_date=date(2023, 10, 16),
            slot_time=time(9, 30),
            capacity=4,
            taken=1
        ),
    ]

    for slot in slots:
        db.add(slot)

    db.commit()
    return slots

def test_search_slots_no_filters(client: TestClient, db: Session, test_slots):
    """Test searching slots without filters."""
    response = client.get("/api/slots")
    assert response.status_code == 200
    data = response.json()

    # Should return only slots with available capacity
    assert data["total"] == 3  # All slots except the fully booked one
    assert len(data["items"]) == 3

    # Verify pagination info
    assert data["page"] == 1
    assert data["size"] == 30
    assert data["pages"] == 1

    # Check that fully booked slots are not included
    slot_times = [slot["slot_time"] for slot in data["items"]]
    assert "10:00:00" not in slot_times

def test_search_slots_by_location(client: TestClient, db: Session, test_office, test_slots):
    """Test searching slots filtered by location."""
    response = client.get(f"/api/slots?location={test_office.city}")
    assert response.status_code == 200
    data = response.json()

    # Should only return slots from the specified city with available capacity
    assert data["total"] == 2
    assert len(data["items"]) == 2

    # Verify all returned slots are from the requested city
    for slot in data["items"]:
        assert slot["office_id"] == str(test_office.id)

def test_search_slots_by_date(client: TestClient, db: Session, test_slots):
    """Test searching slots filtered by date."""
    response = client.get("/api/slots?date=2023-10-16")
    assert response.status_code == 200
    data = response.json()

    # Should only return slots from the specified date with available capacity
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["slot_date"] == "2023-10-16"

def test_search_slots_pagination(client: TestClient, db: Session, test_slots):
    """Test slot search pagination."""
    response = client.get("/api/slots?page=1&size=2")
    assert response.status_code == 200
    data = response.json()

    # Should return only 2 slots due to size parameter
    assert data["total"] == 3  # Total count is still 3
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["size"] == 2
    assert data["pages"] == 2  # 3 items with size 2 needs 2 pages

def test_search_slots_invalid_date(client: TestClient):
    """Test slot search with invalid date format."""
    response = client.get("/api/slots?date=invalid-date")
    assert response.status_code == 400
    assert "Invalid date format" in response.json()["detail"]
