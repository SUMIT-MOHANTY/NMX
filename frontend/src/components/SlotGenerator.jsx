import React, { useState, useEffect } from 'react';
import { format } from 'date-fns';
import '../styles/SlotGenerator.css';
import { generateTimeSlots, validateInputs } from '../utils/slotUtils';
import Logger from '../utils/logger';

const logger = new Logger('SlotGenerator');

const SlotGenerator = () => {
  // State management
  const [date, setDate] = useState('');
  const [office, setOffice] = useState('');
  const [startTime, setStartTime] = useState('09:00');
  const [endTime, setEndTime] = useState('17:00');
  const [slotDuration, setSlotDuration] = useState(60); // minutes
  const [capacity, setCapacity] = useState(1);
  const [slots, setSlots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [offices, setOffices] = useState([]);
  const [successMessage, setSuccessMessage] = useState('');

  // Fetch available offices
  useEffect(() => {
    const fetchOffices = async () => {
      try {
        logger.info('Fetching available offices');
        setLoading(true);
        // In a real app, replace with actual API call
        const response = await fetch('/api/offices');

        if (!response.ok) {
          throw new Error(`Failed to fetch offices: ${response.status}`);
        }

        const data = await response.json();
        setOffices(data.offices || []);
      } catch (err) {
        logger.error('Error fetching offices:', err);
        setError('Failed to load offices. Please try again later.');
        setOffices([
          { id: 1, name: 'Office A' },
          { id: 2, name: 'Office B' },
          { id: 3, name: 'Office C' },
        ]); // Fallback data
      } finally {
        setLoading(false);
      }
    };

    fetchOffices();
  }, []);

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    logger.info('Generating slots with params:', { date, office, startTime, endTime, slotDuration, capacity });

    // Reset states
    setError(null);
    setSuccessMessage('');
    setSlots([]);

    try {
      // Validate inputs
      const validationError = validateInputs({
        date,
        office,
        startTime,
        endTime,
        slotDuration,
        capacity
      });

      if (validationError) {
        setError(validationError);
        return;
      }

      setLoading(true);

      // Generate time slots
      const generatedSlots = generateTimeSlots({
        date,
        startTime,
        endTime,
        slotDuration,
        capacity
      });

      setSlots(generatedSlots);
      setSuccessMessage(`Successfully generated ${generatedSlots.length} slots`);
      logger.info('Slots generated successfully', { count: generatedSlots.length });
    } catch (err) {
      logger.error('Error generating slots:', err);
      setError(`Failed to generate slots: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Handle saving slots to the backend
  const handleSaveSlots = async () => {
    if (slots.length === 0) {
      setError('No slots to save');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccessMessage('');

    try {
      logger.info('Saving slots to backend', { count: slots.length });

      // In a real app, replace with actual API call
      const response = await fetch('/api/slots', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          officeId: office,
          slots: slots.map(slot => ({
            start: slot.start,
            end: slot.end,
            capacity: slot.capacity
          }))
        }),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const result = await response.json();
      setSuccessMessage(`Saved ${result.savedCount || slots.length} slots successfully!`);
      logger.info('Slots saved successfully');
    } catch (err) {
      logger.error('Error saving slots:', err);
      setError(`Failed to save slots: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="slot-generator">
      <h1>Slot Generator</h1>

      {/* Error display */}
      {error && <div className="error-message">{error}</div>}

      {/* Success message */}
      {successMessage && <div className="success-message">{successMessage}</div>}

      <form onSubmit={handleSubmit} className="slot-form">
        <div className="form-group">
          <label htmlFor="date">Date:</label>
          <input
            type="date"
            id="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="office">Office:</label>
          <select
            id="office"
            value={office}
            onChange={(e) => setOffice(e.target.value)}
            required
          >
            <option value="">Select an office</option>
            {offices.map(office => (
              <option key={office.id} value={office.id}>
                {office.name}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="startTime">Start Time:</label>
          <input
            type="time"
            id="startTime"
            value={startTime}
            onChange={(e) => setStartTime(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="endTime">End Time:</label>
          <input
            type="time"
            id="endTime"
            value={endTime}
            onChange={(e) => setEndTime(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="slotDuration">Slot Duration (minutes):</label>
          <input
            type="number"
            id="slotDuration"
            value={slotDuration}
            onChange={(e) => setSlotDuration(parseInt(e.target.value, 10))}
            min="15"
            step="15"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="capacity">Capacity per Slot:</label>
          <input
            type="number"
            id="capacity"
            value={capacity}
            onChange={(e) => setCapacity(parseInt(e.target.value, 10))}
            min="1"
            required
          />
        </div>

        <div className="button-group">
          <button type="submit" disabled={loading}>
            {loading ? 'Generating...' : 'Generate Slots'}
          </button>

          {slots.length > 0 && (
            <button
              type="button"
              onClick={handleSaveSlots}
              disabled={loading}
              className="save-button"
            >
              {loading ? 'Saving...' : 'Save Slots'}
            </button>
          )}
        </div>
      </form>

      {/* Display generated slots */}
      {slots.length > 0 && (
        <div className="slots-container">
          <h2>Generated Slots</h2>
          <div className="slots-grid">
            {slots.map((slot, index) => (
              <div key={index} className="slot-item">
                <span>Start: {format(new Date(slot.start), 'HH:mm')}</span>
                <span>End: {format(new Date(slot.end), 'HH:mm')}</span>
                <span>Capacity: {slot.capacity}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SlotGenerator;
