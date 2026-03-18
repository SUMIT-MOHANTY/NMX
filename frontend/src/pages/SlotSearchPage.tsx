import React from 'react';
import SlotSearch from '../components/SlotSearch';
import { useNavigate } from 'react-router-dom';

const SlotSearchPage: React.FC = () => {
  const navigate = useNavigate();

  const handleSlotSelect = (slot: any) => {
    // Navigate to booking page with selected slot
    navigate(`/booking/new?slotId=${slot.id}`);
  };

  return (
    <div className="page-container">
      <h1>Find Available Appointment Slots</h1>
      <p className="page-description">
        Search for available passport appointment slots by location and date.
        Once you find a suitable slot, select it to proceed with booking.
      </p>

      <SlotSearch onSlotSelect={handleSlotSelect} />
    </div>
  );
};

export default SlotSearchPage;
