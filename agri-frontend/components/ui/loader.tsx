import React from 'react'
import { cn } from '../../lib/utils'

interface LoaderProps extends React.HTMLAttributes<HTMLDivElement> {
  size?: 'sm' | 'md' | 'lg'
  variant?: 'default' | 'primary' | 'muted'
}

const Loader = React.forwardRef<HTMLDivElement, LoaderProps>(
  ({ className, size = 'md', variant = 'default', ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          'animate-spin rounded-full border-2 border-current border-t-transparent',
          size === 'sm' && 'h-4 w-4',
          size === 'md' && 'h-6 w-6',
          size === 'lg' && 'h-8 w-8',
          variant === 'default' && 'text-foreground',
          variant === 'primary' && 'text-primary',
          variant === 'muted' && 'text-muted-foreground',
          className
        )}
        {...props}
      >
        <span className="sr-only">Loading...</span>
      </div>
    )
  }
)
Loader.displayName = 'Loader'

export { Loader }
export type { LoaderProps }
