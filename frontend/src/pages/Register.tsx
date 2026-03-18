import React from 'react';
import RegistrationForm from '../components/auth/RegistrationForm';

const Register: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900">Passport Appointment System</h1>
          <p className="mt-2 text-sm text-gray-600">
            Create your account to book passport appointments
          </p>
        </div>
        <RegistrationForm />
      </div>
    </div>
  );
};

export default Register;
