import React, { useState, useEffect } from 'react';
import { useApi } from '../hooks/useApi';
import { format } from 'date-fns';

interface Slot {
  id: string;
  office_id: string;
  slot_date: string;
  slot_time: string;
  capacity: number;
  taken: number;
  available: number;
}

interface SlotSearchResponse {
  items: Slot[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

interface SlotSearchProps {
  onSlotSelect?: (slot: Slot) => void;
}

const SlotSearch: React.FC<SlotSearchProps> = ({ onSlotSelect }) => {
  const [location, setLocation] = useState<string>('');
  const [date, setDate] = useState<string>('');
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [pageSize] = useState<number>(10);

  const { data, loading, error, fetchData } = useApi<SlotSearchResponse>();

  // Format time to show in a user-friendly way (e.g., "09:00")
  const formatTime = (timeString: string): string => {
    return timeString.substring(0, 5);
  };

  // Format date to show in a user-friendly way
  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString();
  };

  const handleSearch = () => {
    let searchParams = new URLSearchParams();

    if (location) searchParams.append('location', location);
    if (date) searchParams.append('date', date);

    searchParams.append('page', currentPage.toString());
    searchParams.append('size', pageSize.toString());

    fetchData(`/api/slots?${searchParams.toString()}`);
  };

  // Search on initial load, page change, or when search button is clicked
  useEffect(() => {
    handleSearch();
  }, [currentPage]);

  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage);
  };

  return (
    <div className="slot-search-container">
      <h2>Search Available Appointment Slots</h2>

      <div className="search-form">
        <div className="form-group">
          <label htmlFor="location">Location:</label>
          <input
            type="text"
            id="location"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="Enter location (e.g., London)"
            className="form-control"
          />
        </div>

        <div className="form-group">
          <label htmlFor="date">Date:</label>
          <input
            type="date"
            id="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="form-control"
          />
        </div>

        <button
          onClick={() => {
            setCurrentPage(1); // Reset to first page when new search is performed
            handleSearch();
          }}
          className="btn btn-primary"
          disabled={loading}
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          Error: {error.message || 'Failed to load slots. Please try again.'}
        </div>
      )}

      {data && (
        <div className="search-results">
          <h3>Available Slots ({data.total})</h3>

          {data.items.length === 0 ? (
            <p>No available slots match your criteria. Try different search parameters.</p>
          ) : (
            <table className="slots-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Time</th>
                  <th>Available Slots</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((slot) => (
                  <tr key={slot.id}>
                    <td>{formatDate(slot.slot_date)}</td>
                    <td>{formatTime(slot.slot_time)}</td>
                    <td>{slot.available} of {slot.capacity}</td>
                    <td>
                      {onSlotSelect && (
                        <button
                          onClick={() => onSlotSelect(slot)}
                          className="btn btn-sm btn-success"
                        >
                          Select
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          {/* Pagination controls */}
          {data.pages > 1 && (
            <div className="pagination">
              <button
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1 || loading}
                className="btn btn-sm btn-outline-primary"
              >
                Previous
              </button>

              <span className="page-info">
                Page {currentPage} of {data.pages}
              </span>

              <button
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === data.pages || loading}
                className="btn btn-sm btn-outline-primary"
              >
                Next
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SlotSearch;
