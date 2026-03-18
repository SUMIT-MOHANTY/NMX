/**
 * Utility functions for slot generation and validation
 */

/**
 * Validates input parameters for slot generation
 * @param {Object} params - Parameters to validate
 * @returns {string|null} Error message or null if valid
 */
export const validateInputs = ({ date, office, startTime, endTime, slotDuration, capacity }) => {
  // Check required fields
  if (!date) return 'Date is required';
  if (!office) return 'Office is required';
  if (!startTime) return 'Start time is required';
  if (!endTime) return 'End time is required';

  // Check numeric values
  if (slotDuration <= 0) return 'Slot duration must be positive';
  if (capacity <= 0) return 'Capacity must be positive';

  // Validate date is not in the past
  const selectedDate = new Date(date);
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  if (selectedDate < today) {
    return 'Cannot select a date in the past';
  }

  // Parse time strings to compare
  const [startHour, startMinute] = startTime.split(':').map(Number);
  const [endHour, endMinute] = endTime.split(':').map(Number);

  const startDateTime = new Date(selectedDate);
  startDateTime.setHours(startHour, startMinute, 0, 0);

  const endDateTime = new Date(selectedDate);
  endDateTime.setHours(endHour, endMinute, 0, 0);

  if (endDateTime <= startDateTime) {
    return 'End time must be after start time';
  }

  return null;
};

/**
 * Generates time slots based on provided parameters
 * @param {Object} params - Parameters for slot generation
 * @returns {Array} Array of generated time slots
 */
export const generateTimeSlots = ({ date, startTime, endTime, slotDuration, capacity }) => {
  const slots = [];
  const selectedDate = new Date(date);

  // Parse start and end times
  const [startHour, startMinute] = startTime.split(':').map(Number);
  const [endHour, endMinute] = endTime.split(':').map(Number);

  const startDateTime = new Date(selectedDate);
  startDateTime.setHours(startHour, startMinute, 0, 0);

  const endDateTime = new Date(selectedDate);
  endDateTime.setHours(endHour, endMinute, 0, 0);

  // Generate slots
  let currentSlotStart = new Date(startDateTime);

  while (currentSlotStart < endDateTime) {
    const slotEnd = new Date(currentSlotStart.getTime() + slotDuration * 60 * 1000);

    // Don't create slots that extend beyond the end time
    if (slotEnd > endDateTime) {
      break;
    }

    slots.push({
      start: currentSlotStart.toISOString(),
      end: slotEnd.toISOString(),
      capacity: capacity
    });

    // Move to next slot start time
    currentSlotStart = slotEnd;
  }

  return slots;
};

/**
 * Format a date object to a time string (HH:MM)
 * @param {Date} date - The date object
 * @returns {string} Formatted time string
 */
export const formatTime = (date) => {
  const hours = date.getHours().toString().padStart(2, '0');
  const minutes = date.getMinutes().toString().padStart(2, '0');
  return `${hours}:${minutes}`;
};
