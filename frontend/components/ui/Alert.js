import { cn } from '@/lib/utils';
import { X, AlertCircle, CheckCircle, Info, AlertTriangle } from 'lucide-react';

export function Alert({ 
  children, 
  variant = 'info', 
  className,
  onClose,
  ...props 
}) {
  const variants = {
    info: {
      container: 'bg-blue-50 border-blue-200 text-blue-800',
      icon: <Info className="w-5 h-5" />
    },
    success: {
      container: 'bg-green-50 border-green-200 text-green-800',
      icon: <CheckCircle className="w-5 h-5" />
    },
    warning: {
      container: 'bg-yellow-50 border-yellow-200 text-yellow-800',
      icon: <AlertTriangle className="w-5 h-5" />
    },
    danger: {
      container: 'bg-red-50 border-red-200 text-red-800',
      icon: <AlertCircle className="w-5 h-5" />
    }
  };
  
  const config = variants[variant];
  
  return (
    <div 
      className={cn(
        'flex items-start gap-3 p-4 border rounded-lg',
        config.container,
        className
      )}
      {...props}
    >
      <div className="flex-shrink-0">{config.icon}</div>
      <div className="flex-1">{children}</div>
      {onClose && (
        <button
          onClick={onClose}
          className="flex-shrink-0 hover:opacity-70 transition"
        >
          <X className="w-5 h-5" />
        </button>
      )}
    </div>
  );
}
