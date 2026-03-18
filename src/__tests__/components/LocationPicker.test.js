import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import LocationPicker from '../../components/LocationPicker';
import { SlotContextProvider } from '../../context/SlotContext';
import { fetchLocations } from '../../services/api';

// Mock the API service
jest.mock('../../services/api', () => ({
  fetchLocations: jest.fn()
}));

// Mock the logger
jest.mock('../../utils/logger', () => ({
  error: jest.fn(),
  info: jest.fn()
}));

describe('LocationPicker Component', () => {
  beforeEach(() => {
    fetchLocations.mockClear();
    // Mock successful API response
    fetchLocations.mockResolvedValue([
      { id: '1', name: 'Test Location 1' },
      { id: '2', name: 'Test Location 2' }
    ]);
  });

  test('renders loading state initially', async () => {
    render(
      <SlotContextProvider>
        <LocationPicker />
      </SlotContextProvider>
    );

    expect(screen.getByText(/Loading locations.../i)).toBeInTheDocument();

    // Wait for locations to load
    await waitFor(() => {
      expect(screen.queryByText(/Loading locations.../i)).not.toBeInTheDocument();
    });
  });

  test('renders locations after loading', async () => {
    render(
      <SlotContextProvider>
        <LocationPicker />
      </SlotContextProvider>
    );

    // Wait for locations to load
    await waitFor(() => {
      expect(screen.getByText('Test Location 1')).toBeInTheDocument();
      expect(screen.getByText('Test Location 2')).toBeInTheDocument();
    });
  });

  test('handles location selection', async () => {
    const user = userEvent.setup();

    render(
      <SlotContextProvider>
        <LocationPicker />
      </SlotContextProvider>
    );

    // Wait for locations to load
    await waitFor(() => {
      expect(screen.getByLabelText(/Select a location/i)).toBeInTheDocument();
    });

    // Select a location
    await user.selectOptions(screen.getByLabelText(/Select a location/i), '2');

    // Check that the correct option is selected
    expect(screen.getByRole('option', { name: 'Test Location 2' }).selected).toBe(true);
  });

  test('shows error message when API fails', async () => {
    // Mock API failure
    fetchLocations.mockRejectedValue(new Error('API Error'));

    render(
      <SlotContextProvider>
        <LocationPicker />
      </SlotContextProvider>
    );

    // Wait for error message to appear
    await waitFor(() => {
      expect(screen.getByText(/Failed to load locations/i)).toBeInTheDocument();
    });
  });
});
