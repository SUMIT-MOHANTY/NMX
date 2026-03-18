import React from 'react';
import { format } from 'date-fns';
import logger from '../utils/logger';

const SlotCard = ({ slot }) => {
  const { id, startTime, endTime, available, capacity, price } = slot;

  const formatTime = (timeString) => {
    try {
      const date = new Date(timeString);
      return format(date, 'h:mm a');
    } catch (err) {
      logger.error('Error formatting time:', err);
      return timeString;
    }
  };

  const handleBookNow = () => {
    logger.info('Book now clicked for slot:', id);
    // In a real app, this would navigate to booking details or add to cart
    alert(`Booking slot from ${formatTime(startTime)} to ${formatTime(endTime)}`);
  };

  return (
    <div className={`slot-card ${available ? 'available' : 'unavailable'}`}>
      <div className="slot-time">
        <span className="start-time">{formatTime(startTime)}</span>
        <span className="divider">-</span>
        <span className="end-time">{formatTime(endTime)}</span>
      </div>

      <div className="slot-info">
        <span className="capacity">Capacity: {capacity}</span>
        <span className="price">${price.toFixed(2)}</span>
      </div>

      <div className="slot-status">
        {available ? (
          <button
            onClick={handleBookNow}
            className="book-button"
            disabled={!available}
          >
            Book Now
          </button>
        ) : (
          <span className="sold-out">Sold Out</span>
        )}
      </div>
    </div>
  );
};

export default SlotCard;
