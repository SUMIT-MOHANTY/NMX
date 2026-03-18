import React, { useState, useCallback } from 'react';
import {
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Snackbar,
  Alert,
  Stack,
  Typography
} from '@mui/material';

interface ActionsComponentProps {
  /** ID of the item to perform actions on */
  itemId: string | number;
  /** Name or title of the item, used in confirmation dialogs */
  itemName?: string;
  /** Function to call when delete is confirmed */
  onDelete?: (id: string | number) => Promise<void>;
  /** Function to call when export is requested */
  onExport?: (id: string | number) => Promise<void>;
  /** CSS class name for additional styling */
  className?: string;
}

/**
 * A component that provides export and delete functionality with proper error handling
 *
 * Features:
 * - Confirmation dialog before deletion
 * - Loading states during async operations
 * - Error handling and notifications
 * - Accessible button design
 */
const ActionsComponent: React.FC<ActionsComponentProps> = ({
  itemId,
  itemName = 'item',
  onDelete,
  onExport,
  className
}) => {
  // State management
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isLoading, setIsLoading] = useState<'export' | 'delete' | null>(null);
  const [notification, setNotification] = useState<{
    type: 'success' | 'error';
    message: string;
    open: boolean;
  }>({
    type: 'success',
    message: '',
    open: false
  });

  // Logging utility
  const logAction = useCallback((action: string, details: any) => {
    console.log(`[ActionsComponent] ${action}:`, details);
  }, []);

  // Open delete confirmation dialog
  const handleDeleteClick = useCallback(() => {
    logAction('Delete requested', { itemId, itemName });
    setIsDeleteDialogOpen(true);
  }, [itemId, itemName, logAction]);

  // Close delete confirmation dialog
  const handleDeleteCancel = useCallback(() => {
    logAction('Delete cancelled', { itemId });
    setIsDeleteDialogOpen(false);
  }, [itemId, logAction]);

  // Confirm and process deletion
  const handleDeleteConfirm = useCallback(async () => {
    if (!onDelete) {
      logAction('Delete handler missing', { itemId });
      setNotification({
        type: 'error',
        message: 'Delete functionality not available',
        open: true
      });
      return;
    }

    try {
      logAction('Delete confirmed', { itemId });
      setIsLoading('delete');
      await onDelete(itemId);
      setNotification({
        type: 'success',
        message: `${itemName} deleted successfully`,
        open: true
      });
    } catch (error) {
      logAction('Delete failed', { itemId, error });
      setNotification({
        type: 'error',
        message: `Failed to delete ${itemName}: ${error instanceof Error ? error.message : 'Unknown error'}`,
        open: true
      });
    } finally {
      setIsLoading(null);
      setIsDeleteDialogOpen(false);
    }
  }, [itemId, itemName, onDelete, logAction]);

  // Handle export action
  const handleExport = useCallback(async () => {
    if (!onExport) {
      logAction('Export handler missing', { itemId });
      setNotification({
        type: 'error',
        message: 'Export functionality not available',
        open: true
      });
      return;
    }

    try {
      logAction('Export started', { itemId });
      setIsLoading('export');
      await onExport(itemId);
      setNotification({
        type: 'success',
        message: `${itemName} exported successfully`,
        open: true
      });
    } catch (error) {
      logAction('Export failed', { itemId, error });
      setNotification({
        type: 'error',
        message: `Failed to export ${itemName}: ${error instanceof Error ? error.message : 'Unknown error'}`,
        open: true
      });
    } finally {
      setIsLoading(null);
    }
  }, [itemId, itemName, onExport, logAction]);

  // Close notification
  const handleCloseNotification = () => {
    setNotification(prev => ({ ...prev, open: false }));
  };

  return (
    <div className={className} data-testid="actions-component">
      <Stack direction="row" spacing={2}>
        {onExport && (
          <Button
            variant="outlined"
            onClick={handleExport}
            disabled={isLoading !== null}
            startIcon={isLoading === 'export' ? <CircularProgress size={20} /> : null}
            aria-busy={isLoading === 'export'}
            data-testid="export-button"
          >
            {isLoading === 'export' ? 'Exporting...' : 'Export'}
          </Button>
        )}

        {onDelete && (
          <Button
            variant="contained"
            color="error"
            onClick={handleDeleteClick}
            disabled={isLoading !== null}
            startIcon={isLoading === 'delete' ? <CircularProgress size={20} /> : null}
            aria-busy={isLoading === 'delete'}
            data-testid="delete-button"
          >
            {isLoading === 'delete' ? 'Deleting...' : 'Delete'}
          </Button>
        )}
      </Stack>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={isDeleteDialogOpen}
        onClose={handleDeleteCancel}
        aria-labelledby="delete-dialog-title"
        aria-describedby="delete-dialog-description"
      >
        <DialogTitle id="delete-dialog-title">
          Confirm Deletion
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="delete-dialog-description">
            Are you sure you want to delete {itemName}? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel} color="primary">
            Cancel
          </Button>
          <Button
            onClick={handleDeleteConfirm}
            color="error"
            autoFocus
            disabled={isLoading === 'delete'}
          >
            {isLoading === 'delete' ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Notification Snackbar */}
      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={handleCloseNotification}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={handleCloseNotification}
          severity={notification.type}
          sx={{ width: '100%' }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </div>
  );
};

export default ActionsComponent;
