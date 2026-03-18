import pytest
from datetime import date, time
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4

from app.main import app
from app.models.office import Office
from app.models.slot import Slot

client = TestClient(app)

def test_get_available_slots(db: Session):
    # Create test office
    office = Office(id=uuid4(), name="Test Office", location="London")
    db.add(office)
    db.commit()

    # Create test slots
    slots = [
        # Available slot
        Slot(
            id=uuid4(),
            office_id=office.id,
            slot_date=date(2023, 12, 1),
            slot_time=time(9, 0),
            capacity=10,
            taken=5
        ),
        # Fully booked slot
        Slot(
            id=uuid4(),
            office_id=office.id,
            slot_date=date(2023, 12, 1),
            slot_time=time(10, 0),
            capacity=10,
            taken=10
        ),
        # Different date
        Slot(
            id=uuid4(),
            office_id=office.id,
            slot_date=date(2023, 12, 2),
            slot_time=time(9, 0),
            capacity=10,
            taken=2
        ),
    ]

    for slot in slots:
        db.add(slot)
    db.commit()

    # Test without filters
    response = client.get("/api/slots")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2  # Only slots with availability

    # Test with date filter
    response = client.get(f"/api/slots?date=2023-12-01")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1  # Only the available slot on Dec 1

    # Test with location filter
    response = client.get("/api/slots?location=London")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2  # Only available slots in London

    # Test pagination
    response = client.get("/api/slots?page=1&size=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["total"] == 2
    assert data["pages"] == 2

    # Clean up
    for slot in slots:
        db.delete(slot)
    db.delete(office)
    db.commit()
