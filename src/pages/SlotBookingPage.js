import React from 'react';
import LocationPicker from '../components/LocationPicker';
import DatePicker from '../components/DatePicker';
import SlotList from '../components/SlotList';
import { useSlotContext } from '../context/SlotContext';
import './SlotBookingPage.css';

const SlotBookingPage = () => {
  const { selectedLocation, selectedDate } = useSlotContext();

  return (
    <div className="slot-booking-page">
      <div className="filters">
        <LocationPicker />
        <DatePicker />
      </div>

      {selectedLocation && selectedDate ? (
        <div className="selection-summary">
          <p>Showing slots for <strong>{selectedLocation.name}</strong> on <strong>{selectedDate.toLocaleDateString()}</strong></p>
        </div>
      ) : null}

      <SlotList />
    </div>
  );
};

export default SlotBookingPage;
