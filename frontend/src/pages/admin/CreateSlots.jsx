import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuth from '../../../hooks/useAuth';
import axios from 'axios';

const CreateSlots = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [offices, setOffices] = useState([]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  // Form state
  const [formData, setFormData] = useState({
    office_id: '',
    slot_date: '',
    start_time: '08:00',
    end_time: '17:00',
    capacity: 1,
  });

  // Validate that user is admin
  useEffect(() => {
    if (!user || user.role !== 'admin') {
      navigate('/login');
    }
  }, [user, navigate]);

  // Fetch offices for the dropdown
  useEffect(() => {
    const fetchOffices = async () => {
      setLoading(true);
      try {
        const response = await axios.get('/api/offices', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        setOffices(response.data);
      } catch (error) {
        console.error('Error fetching offices:', error);
        setMessage({
          type: 'error',
          text: 'Failed to load offices. Please try again later.'
        });
      } finally {
        setLoading(false);
      }
    };

    fetchOffices();
  }, []);

  // Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  // Generate 30-minute time slots between start and end time
  const generateTimeSlots = (startTime, endTime) => {
    const slots = [];
    const start = new Date(`2000-01-01T${startTime}`);
    const end = new Date(`2000-01-01T${endTime}`);

    // Loop through each 30-minute interval
    let current = new Date(start);
    while (current < end) {
      slots.push(
        current.toTimeString().slice(0, 5) // Format as HH:MM
      );
      current.setMinutes(current.getMinutes() + 30);
    }

    return slots;
  };

  // Validate form data
  const validateForm = () => {
    if (!formData.office_id) {
      setMessage({ type: 'error', text: 'Please select an office.' });
      return false;
    }

    if (!formData.slot_date) {
      setMessage({ type: 'error', text: 'Please select a date.' });
      return false;
    }

    // Ensure date is not in the past
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const selectedDate = new Date(formData.slot_date);
    if (selectedDate < today) {
      setMessage({ type: 'error', text: 'Cannot create slots for past dates.' });
      return false;
    }

    if (formData.start_time >= formData.end_time) {
      setMessage({ type: 'error', text: 'End time must be after start time.' });
      return false;
    }

    if (formData.capacity < 1) {
      setMessage({ type: 'error', text: 'Capacity must be at least 1.' });
      return false;
    }

    return true;
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setSubmitting(true);
    setMessage({ type: '', text: '' });

    try {
      const timeSlots = generateTimeSlots(formData.start_time, formData.end_time);

      // Create batch request payload
      const slotsToCreate = timeSlots.map(time => ({
        office_id: formData.office_id,
        slot_date: formData.slot_date,
        slot_time: time,
        capacity: parseInt(formData.capacity, 10)
      }));

      // Send batch request to create slots
      const response = await axios.post('/api/admin/slots', slotsToCreate, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });

      console.log('Slots created:', response.data);

      setMessage({
        type: 'success',
        text: `Successfully created ${response.data.created} slots.`
      });

      // Reset form
      setFormData({
        office_id: '',
        slot_date: '',
        start_time: '08:00',
        end_time: '17:00',
        capacity: 1,
      });
    } catch (error) {
      console.error('Error creating slots:', error);

      let errorMsg = 'Failed to create slots. Please try again.';
      if (error.response?.data?.detail) {
        errorMsg = error.response.data.detail;
      }

      setMessage({ type: 'error', text: errorMsg });
    } finally {
      setSubmitting(false);
    }
  };

  // Generate time options for select dropdowns
  const generateTimeOptions = () => {
    const options = [];
    let hour = 8;
    let minute = 0;

    // Generate options from 08:00 to 17:00 in 30-minute intervals
    while (hour < 18) {
      const timeString = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
      options.push(
        <option key={timeString} value={timeString}>
          {timeString}
        </option>
      );

      // Increment by 30 minutes
      minute += 30;
      if (minute >= 60) {
        hour += 1;
        minute = 0;
      }
    }

    return options;
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Create Appointment Slots</h1>

      {/* Status Messages */}
      {message.text && (
        <div className={`p-4 mb-4 rounded-md ${message.type === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
          {message.text}
        </div>
      )}

      <div className="bg-white p-6 rounded-lg shadow-md">
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 font-medium mb-2" htmlFor="office_id">
              Office Location
            </label>
            <select
              id="office_id"
              name="office_id"
              className="w-full p-2 border rounded"
              value={formData.office_id}
              onChange={handleChange}
              disabled={loading || submitting}
            >
              <option value="">Select an office</option>
              {offices.map((office) => (
                <option key={office.id} value={office.id}>
                  {office.name}
                </option>
              ))}
            </select>
          </div>

          <div className="mb-4">
            <label className="block text-gray-700 font-medium mb-2" htmlFor="slot_date">
              Date
            </label>
            <input
              type="date"
              id="slot_date"
              name="slot_date"
              className="w-full p-2 border rounded"
              value={formData.slot_date}
              onChange={handleChange}
              disabled={submitting}
              min={new Date().toISOString().split('T')[0]} // Prevents selecting past dates
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-gray-700 font-medium mb-2" htmlFor="start_time">
                Start Time
              </label>
              <select
                id="start_time"
                name="start_time"
                className="w-full p-2 border rounded"
                value={formData.start_time}
                onChange={handleChange}
                disabled={submitting}
              >
                {generateTimeOptions()}
              </select>
            </div>

            <div>
              <label className="block text-gray-700 font-medium mb-2" htmlFor="end_time">
                End Time
              </label>
              <select
                id="end_time"
                name="end_time"
                className="w-full p-2 border rounded"
                value={formData.end_time}
                onChange={handleChange}
                disabled={submitting}
              >
                {generateTimeOptions()}
              </select>
            </div>
          </div>

          <div className="mb-6">
            <label className="block text-gray-700 font-medium mb-2" htmlFor="capacity">
              Capacity (appointments per slot)
            </label>
            <input
              type="number"
              id="capacity"
              name="capacity"
              min="1"
              className="w-full p-2 border rounded"
              value={formData.capacity}
              onChange={handleChange}
              disabled={submitting}
            />
          </div>

          <button
            type="submit"
            className={`w-full py-2 px-4 rounded font-medium ${
              submitting
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            }`}
            disabled={submitting}
          >
            {submitting ? 'Generating Slots...' : 'Generate Slots'}
          </button>
        </form>
      </div>

      {/* Preview Section */}
      {!submitting && formData.slot_date && formData.office_id && (
        <div className="mt-8 bg-gray-50 p-6 rounded-lg">
          <h2 className="text-xl font-semibold mb-4">Slots Preview</h2>
          <p>
            <strong>Date:</strong> {formData.slot_date}
          </p>
          <p>
            <strong>Office:</strong> {offices.find(o => o.id === formData.office_id)?.name || ''}
          </p>
          <p>
            <strong>Time Range:</strong> {formData.start_time} - {formData.end_time}
          </p>
          <p>
            <strong>Capacity per slot:</strong> {formData.capacity}
          </p>
          <p>
            <strong>Slot Count:</strong> {generateTimeSlots(formData.start_time, formData.end_time).length}
          </p>
        </div>
      )}
    </div>
  );
};

export default CreateSlots;
