# OpenTable API

REST API for retrieving available reservation slots filtered by city and date.

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python main.py`

## API Documentation

### Get Available Slots

Retrieves available reservation slots filtered by city and date.

**URL**: `/api/v1/slots`

**Method**: `GET`

**Query Parameters**:
- `city` (required): The city to filter by
- `date` (required): The date to filter by in YYYY-MM-DD format

**Success Response**:
