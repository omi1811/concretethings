import React from 'react';

/**
 * Reusable Form Input Component
 * @param {string} label - Input label
 * @param {string} error - Error message
 * @param {string} type - Input type (text, email, password, etc.)
 * @param {string} className - Additional CSS classes
 * @param {object} props - Other input props (value, onChange, etc.)
 */
export const FormInput = React.memo(({ 
  label, 
  error, 
  type = 'text',
  className = '',
  ...props 
}) => (
  <div className="space-y-1">
    {label && (
      <label className="block text-sm font-medium text-gray-700">
        {label}
      </label>
    )}
    <input
      type={type}
      className={`w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 transition-all ${
        error 
          ? 'border-red-300 focus:ring-red-500' 
          : 'border-gray-300 focus:ring-blue-500'
      } ${className}`}
      {...props}
    />
    {error && (
      <p className="text-xs text-red-600 mt-1">{error}</p>
    )}
  </div>
));

FormInput.displayName = 'FormInput';
