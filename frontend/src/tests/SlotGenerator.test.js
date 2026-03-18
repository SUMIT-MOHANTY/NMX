import { validateInputs, generateTimeSlots } from '../utils/slotUtils';

describe('Slot Generator Utilities', () => {
  describe('validateInputs', () => {
    test('should return null for valid inputs', () => {
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);

      const result = validateInputs({
        date: tomorrow.toISOString().split('T')[0],
        office: '1',
        startTime: '09:00',
        endTime: '17:00',
        slotDuration: 60,
        capacity: 5
      });

      expect(result).toBeNull();
    });

    test('should return error for missing date', () => {
      const result = validateInputs({
        date: '',
        office: '1',
        startTime: '09:00',
        endTime: '17:00',
        slotDuration: 60,
        capacity: 5
      });

      expect(result).toBe('Date is required');
    });

    test('should return error when end time is before start time', () => {
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);

      const result = validateInputs({
        date: tomorrow.toISOString().split('T')[0],
        office: '1',
        startTime: '17:00',
        endTime: '09:00',
        slotDuration: 60,
        capacity: 5
      });

      expect(result).toBe('End time must be after start time');
    });
  });

  describe('generateTimeSlots', () => {
    test('should generate correct number of slots', () => {
      const date = '2023-01-01';
      const startTime = '09:00';
      const endTime = '11:00';
      const slotDuration = 30;
      const capacity = 5;

      const slots = generateTimeSlots({
        date,
        startTime,
        endTime,
        slotDuration,
        capacity
      });

      // Should create 4 slots of 30 minutes each (9:00-9:30, 9:30-10:00, 10:00-10:30, 10:30-11:00)
      expect(slots.length).toBe(4);
    });

    test('should set correct capacity for each slot', () => {
      const date = '2023-01-01';
      const startTime = '09:00';
      const endTime = '11:00';
      const slotDuration = 60;
      const capacity = 10;

      const slots = generateTimeSlots({
        date,
        startTime,
        endTime,
        slotDuration,
        capacity
      });

      slots.forEach(slot => {
        expect(slot.capacity).toBe(capacity);
      });
    });
  });
});
