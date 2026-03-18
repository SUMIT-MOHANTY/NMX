/**
 * Utility functions for validating data
 */

// Check if a value is empty (null, undefined, empty string, empty array)
export const isEmpty = (value) => {
  if (value === null || value === undefined) return true;
  if (typeof value === 'string') return value.trim() === '';
  if (Array.isArray(value)) return value.length === 0;
  if (typeof value === 'object') return Object.keys(value).length === 0;
  return false;
};

// Validate that a date is in the present or future
export const isValidFutureDate = (date) => {
  if (!(date instanceof Date) || isNaN(date)) return false;
  const now = new Date();
  now.setHours(0, 0, 0, 0);
  date.setHours(0, 0, 0, 0);
  return date >= now;
};

// Validate that a string is a valid location ID format
export const isValidLocationId = (id) => {
  // In a real app, this might check against a specific format
  return typeof id === 'string' && id.trim() !== '';
};

// Validate that a slot object has all required fields and valid data
export const isValidSlot = (slot) => {
  if (!slot || typeof slot !== 'object') return false;

  // Check required fields
  const requiredFields = ['id', 'startTime', 'endTime', 'available', 'capacity', 'price'];
  for (const field of requiredFields) {
    if (!(field in slot)) return false;
  }

  // Type checking
  if (typeof slot.id !== 'string') return false;
  if (!(new Date(slot.startTime) instanceof Date)) return false;
  if (!(new Date(slot.endTime) instanceof Date)) return false;
  if (typeof slot.available !== 'boolean') return false;
  if (typeof slot.capacity !== 'number' || slot.capacity < 0) return false;
  if (typeof slot.price !== 'number' || slot.price < 0) return false;

  // Time validation: end time should be after start time
  const startTime = new Date(slot.startTime);
  const endTime = new Date(slot.endTime);
  if (endTime <= startTime) return false;

  return true;
};
