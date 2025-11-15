import React from 'react';

/**
 * Reusable Alert Component
 * @param {string} type - Alert type (error, success, warning, info)
 * @param {ReactNode} children - Alert content
 * @param {function} onClose - Close callback
 * @param {string} className - Additional CSS classes
 */
export const Alert = React.memo(({ 
  type = 'info', 
  children, 
  onClose,
  className = ''
}) => {
  const styles = {
    error: {
      bg: 'bg-red-50',
      border: 'border-red-200',
      text: 'text-red-800',
      icon: '❌',
    },
    success: {
      bg: 'bg-green-50',
      border: 'border-green-200',
      text: 'text-green-800',
      icon: '✅',
    },
    warning: {
      bg: 'bg-yellow-50',
      border: 'border-yellow-200',
      text: 'text-yellow-800',
      icon: '⚠️',
    },
    info: {
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      text: 'text-blue-800',
      icon: 'ℹ️',
    },
  };

  const style = styles[type] || styles.info;
  
  return (
    <div className={`p-4 border rounded-lg flex items-start gap-3 ${style.bg} ${style.border} ${style.text} ${className}`}>
      <span className="text-lg">{style.icon}</span>
      <span className="flex-1">{children}</span>
      {onClose && (
        <button 
          onClick={onClose} 
          className="text-current opacity-70 hover:opacity-100 transition-opacity text-xl leading-none"
          aria-label="Close alert"
        >
          ×
        </button>
      )}
    </div>
  );
});

Alert.displayName = 'Alert';
