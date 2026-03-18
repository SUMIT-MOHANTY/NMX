import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import SlotCard from '../../components/SlotCard';
import { format } from 'date-fns';

// Mock the window.alert
const mockAlert = jest.fn();
window.alert = mockAlert;

// Mock the logger
jest.mock('../../utils/logger', () => ({
  info: jest.fn(),
  error: jest.fn()
}));

describe('SlotCard Component', () => {
  const mockAvailableSlot = {
    id: 'slot-1',
    startTime: '2023-09-01T10:00:00.000Z',
    endTime: '2023-09-01T11:00:00.000Z',
    available: true,
    capacity: 5,
    price: 25.99
  };

  const mockSoldOutSlot = {
    id: 'slot-2',
    startTime: '2023-09-01T12:00:00.000Z',
    endTime: '2023-09-01T13:00:00.000Z',
    available: false,
    capacity: 0,
    price: 30
  };

  test('renders available slot correctly', () => {
    render(<SlotCard slot={mockAvailableSlot} />);

    expect(screen.getByText(/10:00 AM/i)).toBeInTheDocument();
    expect(screen.getByText(/11:00 AM/i)).toBeInTheDocument();
    expect(screen.getByText(/Capacity: 5/i)).toBeInTheDocument();
    expect(screen.getByText(/\$25.99/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Book Now/i })).toBeInTheDocument();
    expect(screen.queryByText(/Sold Out/i)).not.toBeInTheDocument();
  });

  test('renders sold out slot correctly', () => {
    render(<SlotCard slot={mockSoldOutSlot} />);

    expect(screen.getByText(/12:00 PM/i)).toBeInTheDocument();
    expect(screen.getByText(/1:00 PM/i)).toBeInTheDocument();
    expect(screen.getByText(/Capacity: 0/i)).toBeInTheDocument();
    expect(screen.getByText(/\$30.00/i)).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /Book Now/i })).not.toBeInTheDocument();
    expect(screen.getByText(/Sold Out/i)).toBeInTheDocument();
  });

  test('handles "Book Now" button click', async () => {
    const user = userEvent.setup();

    render(<SlotCard slot={mockAvailableSlot} />);

    const bookButton = screen.getByRole('button', { name: /Book Now/i });
    await user.click(bookButton);

    // Check if alert was called with expected message
    expect(mockAlert).toHaveBeenCalledWith('Booking slot from 10:00 AM to 11:00 AM');
  });

  test('handles invalid date formats gracefully', () => {
    const invalidSlot = {
      ...mockAvailableSlot,
      startTime: 'invalid-date',
      endTime: 'invalid-date'
    };

    render(<SlotCard slot={invalidSlot} />);

    // Should still render the component without crashing
    expect(screen.getByText(/invalid-date/i)).toBeInTheDocument();
  });
});
