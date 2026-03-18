import {
  isEmpty,
  isValidFutureDate,
  isValidLocationId,
  isValidSlot
} from '../../utils/validation';

describe('Validation Utils', () => {
  describe('isEmpty', () => {
    test('returns true for null and undefined', () => {
      expect(isEmpty(null)).toBe(true);
      expect(isEmpty(undefined)).toBe(true);
    });

    test('returns true for empty string', () => {
      expect(isEmpty('')).toBe(true);
      expect(isEmpty('   ')).toBe(true);
    });

    test('returns true for empty array', () => {
      expect(isEmpty([])).toBe(true);
    });

    test('returns true for empty object', () => {
      expect(isEmpty({})).toBe(true);
    });

    test('returns false for non-empty values', () => {
      expect(isEmpty('test')).toBe(false);
      expect(isEmpty([1, 2, 3])).toBe(false);
      expect(isEmpty({ key: 'value' })).toBe(false);
      expect(isEmpty(0)).toBe(false);
      expect(isEmpty(false)).toBe(false);
    });
  });

  describe('isValidFutureDate', () => {
    test('returns false for invalid dates', () => {
      expect(isValidFutureDate(null)).toBe(false);
      expect(isValidFutureDate('2023-09-01')).toBe(false);
      expect(isValidFutureDate(new Date('invalid'))).toBe(false);
    });

    test('returns true for today and future dates', () => {
      const today = new Date();
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);

      expect(isValidFutureDate(today)).toBe(true);
      expect(isValidFutureDate(tomorrow)).toBe(true);
    });

    test('returns false for past dates', () => {
      const yesterday = new Date();
      yesterday.setDate(yesterday.getDate() - 1);

      expect(isValidFutureDate(yesterday)).toBe(false);
    });
  });

  describe('isValidLocationId', () => {
    test('returns false for invalid location IDs', () => {
      expect(isValidLocationId(null)).toBe(false);
      expect(isValidLocationId(undefined)).toBe(false);
      expect(isValidLocationId('')).toBe(false);
      expect(isValidLocationId('   ')).toBe(false);
      expect(isValidLocationId(123)).toBe(false);
    });

    test('returns true for valid location IDs', () => {
      expect(isValidLocationId('location-1')).toBe(true);
      expect(isValidLocationId('123')).toBe(true);
    });
  });

  describe('isValidSlot', () => {
    const validSlot = {
      id: 'slot-1',
      startTime: '2023-09-01T10:00:00Z',
      endTime: '2023-09-01T11:00:00Z',
      available: true,
      capacity: 5,
      price: 25.99
    };

    test('returns true for valid slot objects', () => {
      expect(isValidSlot(validSlot)).toBe(true);
    });

    test('returns false for missing required fields', () => {
      expect(isValidSlot({ ...validSlot, id: undefined })).toBe(false);
      expect(isValidSlot({ ...validSlot, startTime: undefined })).toBe(false);
      expect(isValidSlot({ ...validSlot, endTime: undefined })).toBe(false);
    });

    test('returns false for invalid field types', () => {
      expect(isValidSlot({ ...validSlot, id: 123 })).toBe(false);
      expect(isValidSlot({ ...validSlot, available: 'yes' })).toBe(false);
      expect(isValidSlot({ ...validSlot, capacity: '5' })).toBe(false);
      expect(isValidSlot({ ...validSlot, price: '25.99' })).toBe(false);
    });

    test('returns false if end time is before start time', () => {
      expect(isValidSlot({
        ...validSlot,
        startTime: '2023-09-01T11:00:00Z',
        endTime: '2023-09-01T10:00:00Z'
      })).toBe(false);
    });

    test('returns false for negative capacity or price', () => {
      expect(isValidSlot({ ...validSlot, capacity: -1 })).toBe(false);
      expect(isValidSlot({ ...validSlot, price: -10 })).toBe(false);
    });
  });
});
