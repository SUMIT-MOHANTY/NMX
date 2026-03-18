import React from 'react';
import ReactDatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { useSlotContext } from '../context/SlotContext';
import { isAfter, startOfDay } from 'date-fns';
import logger from '../utils/logger';

const DatePicker = () => {
  const { selectedDate, setSelectedDate } = useSlotContext();

  const handleDateChange = (date) => {
    setSelectedDate(date);
    logger.info('Date selected:', date);
  };

  // Only allow dates from today onwards
  const isDateDisabled = (date) => {
    const today = startOfDay(new Date());
    return !isAfter(date, today) && date.getDate() !== today.getDate();
  };

  return (
    <div className="date-picker">
      <label htmlFor="date-picker">Select Date:</label>
      <ReactDatePicker
        id="date-picker"
        selected={selectedDate}
        onChange={handleDateChange}
        filterDate={date => !isDateDisabled(date)}
        dateFormat="MMMM d, yyyy"
        minDate={new Date()}
        placeholderText="Select a date"
        aria-label="Select a date"
      />
    </div>
  );
};

export default DatePicker;
