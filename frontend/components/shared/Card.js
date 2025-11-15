import React from 'react';

/**
 * Reusable Card Component
 * @param {ReactNode} children - Card content
 * @param {string} title - Optional card title
 * @param {string} className - Additional CSS classes
 * @param {boolean} hover - Enable hover effect
 * @param {function} onClick - Click handler
 */
export const Card = React.memo(({ 
  children,
  title,
  className = '',
  hover = false,
  onClick,
  ...props
}) => {
  const hoverClass = hover ? 'hover:shadow-lg hover:scale-[1.02] transition-all cursor-pointer' : '';
  const clickable = onClick ? 'cursor-pointer' : '';
  
  return (
    <div 
      className={`bg-white rounded-lg shadow-md border border-gray-200 p-6 ${hoverClass} ${clickable} ${className}`}
      onClick={onClick}
      {...props}
    >
      {title && (
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      )}
      {children}
    </div>
  );
});

Card.displayName = 'Card';
