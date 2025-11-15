import React from 'react';

/**
 * Reusable Button Component with loading state
 * @param {boolean} loading - Show loading spinner
 * @param {string} variant - Button style (primary, secondary, danger, success)
 * @param {string} size - Button size (sm, md, lg)
 * @param {string} className - Additional CSS classes
 * @param {ReactNode} children - Button content
 */
export const Button = React.memo(({ 
  loading = false,
  variant = 'primary',
  size = 'md',
  className = '',
  children,
  disabled,
  ...props 
}) => {
  const variants = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white focus:ring-blue-500',
    secondary: 'bg-gray-600 hover:bg-gray-700 text-white focus:ring-gray-500',
    danger: 'bg-red-600 hover:bg-red-700 text-white focus:ring-red-500',
    success: 'bg-green-600 hover:bg-green-700 text-white focus:ring-green-500',
    outline: 'bg-white border-2 border-gray-300 hover:bg-gray-50 text-gray-700 focus:ring-gray-500',
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-3',
    lg: 'px-6 py-4 text-lg',
  };
  
  return (
    <button
      className={`rounded-lg font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform active:scale-[0.98] ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={loading || disabled}
      {...props}
    >
      {loading ? (
        <span className="flex items-center justify-center gap-2">
          <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
            <circle 
              className="opacity-25" 
              cx="12" 
              cy="12" 
              r="10" 
              stroke="currentColor" 
              strokeWidth="4" 
              fill="none" 
            />
            <path 
              className="opacity-75" 
              fill="currentColor" 
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" 
            />
          </svg>
          <span>Loading...</span>
        </span>
      ) : children}
    </button>
  );
});

Button.displayName = 'Button';
