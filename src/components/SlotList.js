import React, { useEffect, useState } from 'react';
import SlotCard from './SlotCard';
import { fetchSlots } from '../services/api';
import { useSlotContext } from '../context/SlotContext';
import logger from '../utils/logger';

const SlotList = () => {
  const [slots, setSlots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { selectedLocation, selectedDate } = useSlotContext();

  useEffect(() => {
    const getSlots = async () => {
      // Only fetch slots if both location and date are selected
      if (!selectedLocation || !selectedDate) {
        setSlots([]);
        return;
      }

      setLoading(true);
      try {
        const data = await fetchSlots(selectedLocation.id, selectedDate);
        setSlots(data);
        setError(null);
        logger.info(`Loaded ${data.length} slots for location ${selectedLocation.id} on ${selectedDate}`);
      } catch (err) {
        setError('Failed to load available slots');
        logger.error('Error fetching slots:', err);
      } finally {
        setLoading(false);
      }
    };

    getSlots();
  }, [selectedLocation, selectedDate]);

  if (!selectedLocation || !selectedDate) {
    return <div className="instruction-message">Please select both a location and date to view available slots.</div>;
  }

  if (loading) return <div className="loading">Loading slots...</div>;
  if (error) return <div className="error-message">{error}</div>;
  if (slots.length === 0) return <div className="no-slots">No slots available for the selected date and location.</div>;

  return (
    <div className="slot-list">
      <h2>Available Slots</h2>
      <div className="slots-container">
        {slots.map(slot => (
          <SlotCard key={slot.id} slot={slot} />
        ))}
      </div>
    </div>
  );
};

export default SlotList;
