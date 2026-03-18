import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ActionsComponent from './ActionsComponent';

// Mock implementations for handlers
const mockExport = jest.fn(() => Promise.resolve());
const mockDelete = jest.fn(() => Promise.resolve());
const mockExportError = jest.fn(() => Promise.reject(new Error('Export failed')));
const mockDeleteError = jest.fn(() => Promise.reject(new Error('Delete failed')));

describe('ActionsComponent', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders export and delete buttons', () => {
    render(
      <ActionsComponent
        itemId="123"
        itemName="Test Item"
        onExport={mockExport}
        onDelete={mockDelete}
      />
    );

    expect(screen.getByText('Export')).toBeInTheDocument();
    expect(screen.getByText('Delete')).toBeInTheDocument();
  });

  test('opens delete confirmation dialog when delete button clicked', () => {
    render(
      <ActionsComponent
        itemId="123"
        itemName="Test Item"
        onExport={mockExport}
        onDelete={mockDelete}
      />
    );

    fireEvent.click(screen.getByText('Delete'));
    expect(screen.getByText('Confirm Deletion')).toBeInTheDocument();
    expect(screen.getByText(/Are you sure you want to delete Test Item/)).toBeInTheDocument();
  });

  test('calls onExport when export button clicked', async () => {
    render(
      <ActionsComponent
        itemId="123"
        itemName="Test Item"
        onExport={mockExport}
        onDelete={mockDelete}
      />
    );

    fireEvent.click(screen.getByText('Export'));
    await waitFor(() => {
      expect(mockExport).toHaveBeenCalledWith('123');
    });
  });

  test('calls onDelete when delete is confirmed', async () => {
    render(
      <ActionsComponent
        itemId="123"
        itemName="Test Item"
        onExport={mockExport}
        onDelete={mockDelete}
      />
    );

    fireEvent.click(screen.getByText('Delete'));
    fireEvent.click(screen.getByText('Delete').closest('button'));

    await waitFor(() => {
      expect(mockDelete).toHaveBeenCalledWith('123');
    });
  });

  test('shows error notification when export fails', async () => {
    render(
      <ActionsComponent
        itemId="123"
        itemName="Test Item"
        onExport={mockExportError}
        onDelete={mockDelete}
      />
    );

    fireEvent.click(screen.getByText('Export'));

    await waitFor(() => {
      expect(screen.getByText(/Failed to export Test Item/)).toBeInTheDocument();
    });
  });

  test('shows error notification when delete fails', async () => {
    render(
      <ActionsComponent
        itemId="123"
        itemName="Test Item"
        onExport={mockExport}
        onDelete={mockDeleteError}
      />
    );

    fireEvent.click(screen.getByText('Delete'));
    fireEvent.click(screen.getByText('Delete').closest('button'));

    await waitFor(() => {
      expect(screen.getByText(/Failed to delete Test Item/)).toBeInTheDocument();
    });
  });
});
