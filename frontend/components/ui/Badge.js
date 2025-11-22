import { cn } from '@/lib/utils';

export function Badge({ children, variant = 'default', className, ...props }) {
  const variants = {
    default: 'bg-secondary text-secondary-foreground',
    success: 'bg-green-500/15 text-green-700 dark:text-green-400',
    warning: 'bg-yellow-500/15 text-yellow-700 dark:text-yellow-400',
    danger: 'bg-destructive/15 text-destructive',
    info: 'bg-blue-500/15 text-blue-700 dark:text-blue-400',
    synced: 'bg-green-500/15 text-green-700 dark:text-green-400',
    offline: 'bg-destructive/15 text-destructive',
    syncing: 'bg-blue-500/15 text-blue-700 dark:text-blue-400',
    pending: 'bg-yellow-500/15 text-yellow-700 dark:text-yellow-400'
  };

  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium transition-colors',
        variants[variant],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}

export default Badge;
