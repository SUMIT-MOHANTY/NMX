import React from 'react';
import { Paper, Typography, Box } from '@mui/material';
import ActionsComponent from './ActionsComponent';

/**
 * Example component demonstrating how to use ActionsComponent
 */
const ActionsComponentExample: React.FC = () => {
  // Example handlers with proper logging and error handling
  const handleExport = async (id: string | number) => {
    console.log(`Exporting item ${id}`);
    // Simulate API call with random success/failure
    await new Promise<void>((resolve, reject) => {
      setTimeout(() => {
        if (Math.random() > 0.3) {
          console.log(`Export completed for item ${id}`);
          resolve();
        } else {
          console.error(`Export failed for item ${id}`);
          reject(new Error("Failed to connect to export service"));
        }
      }, 1500);
    });
  };

  const handleDelete = async (id: string | number) => {
    console.log(`Deleting item ${id}`);
    // Simulate API call with random success/failure
    await new Promise<void>((resolve, reject) => {
      setTimeout(() => {
        if (Math.random() > 0.3) {
          console.log(`Delete completed for item ${id}`);
          resolve();
        } else {
          console.error(`Delete failed for item ${id}`);
          reject(new Error("Permission denied"));
        }
      }, 1500);
    });
  };

  return (
    <Paper sx={{ p: 3, maxWidth: 600, mx: 'auto', my: 4 }}>
      <Typography variant="h5" gutterBottom>
        Item Actions Example
      </Typography>

      <Box sx={{ mb: 4 }}>
        <Typography variant="body1" paragraph>
          This example shows the ActionsComponent with both export and delete functionality.
          Click the buttons to see loading states and notifications.
        </Typography>
        <ActionsComponent
          itemId="example-123"
          itemName="Example Item"
          onExport={handleExport}
          onDelete={handleDelete}
        />
      </Box>

      <Box sx={{ mb: 4 }}>
        <Typography variant="body1" paragraph>
          This example shows the ActionsComponent with only export functionality.
        </Typography>
        <ActionsComponent
          itemId="export-only-123"
          itemName="Export-Only Item"
          onExport={handleExport}
        />
      </Box>

      <Box>
        <Typography variant="body1" paragraph>
          This example shows the ActionsComponent with only delete functionality.
        </Typography>
        <ActionsComponent
          itemId="delete-only-123"
          itemName="Delete-Only Item"
          onDelete={handleDelete}
        />
      </Box>
    </Paper>
  );
};

export default ActionsComponentExample;
