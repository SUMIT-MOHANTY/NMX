import React, { useState, useEffect } from 'react';
import { useSlotContext } from '../context/SlotContext';
import { fetchLocations } from '../services/api';
import logger from '../utils/logger';

const LocationPicker = () => {
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { selectedLocation, setSelectedLocation } = useSlotContext();

  useEffect(() => {
    const getLocations = async () => {
      setLoading(true);
      try {
        const data = await fetchLocations();
        setLocations(data);
        setError(null);
      } catch (err) {
        setError('Failed to load locations');
        logger.error('Error fetching locations:', err);
      } finally {
        setLoading(false);
      }
    };

    getLocations();
  }, []);

  const handleLocationChange = (e) => {
    const locationId = e.target.value;
    const location = locations.find(loc => loc.id === locationId);
    setSelectedLocation(location);
    logger.info('Location selected:', location);
  };

  if (loading) return <div>Loading locations...</div>;
  if (error) return <div className="error-message">{error}</div>;

  return (
    <div className="location-picker">
      <label htmlFor="location-select">Select Location:</label>
      <select
        id="location-select"
        value={selectedLocation?.id || ''}
        onChange={handleLocationChange}
        aria-label="Select a location"
      >
        <option value="">-- Select a location --</option>
        {locations.map(location => (
          <option key={location.id} value={location.id}>
            {location.name}
          </option>
        ))}
      </select>
    </div>
  );
};

export default LocationPicker;
