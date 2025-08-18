"use client";

interface LoadingDotsProps {
  size?: 'sm' | 'md' | 'lg';
  color?: 'primary' | 'secondary' | 'green';
  className?: string;
}

export function LoadingDots({ size = 'md', color = 'primary', className = '' }: LoadingDotsProps) {
  const sizeClasses = {
    sm: 'w-1 h-1',
    md: 'w-2 h-2',
    lg: 'w-3 h-3'
  };

  const colorClasses = {
    primary: 'bg-primary',
    secondary: 'bg-secondary',
    green: 'bg-green-500'
  };

  return (
    <div className={`flex space-x-1 ${className}`}>
      <div
        className={`${sizeClasses[size]} ${colorClasses[color]} rounded-full animate-bounce`}
        style={{ animationDelay: '0ms' }}
      />
      <div
        className={`${sizeClasses[size]} ${colorClasses[color]} rounded-full animate-bounce`}
        style={{ animationDelay: '150ms' }}
      />
      <div
        className={`${sizeClasses[size]} ${colorClasses[color]} rounded-full animate-bounce`}
        style={{ animationDelay: '300ms' }}
      />
    </div>
  );
}

interface QualityIndicatorProps {
  score: number;
  label: string;
  className?: string;
}

export function QualityIndicator({ score, label, className = '' }: QualityIndicatorProps) {
  const getColor = (score: number) => {
    if (score >= 0.9) return 'text-green-600 bg-green-50 border-green-200';
    if (score >= 0.8) return 'text-blue-600 bg-blue-50 border-blue-200';
    if (score >= 0.7) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };

  const getIcon = (score: number) => {
    if (score >= 0.9) return '🌟';
    if (score >= 0.8) return '✅';
    if (score >= 0.7) return '⚠️';
    return '❌';
  };

  return (
    <div className={`inline-flex items-center gap-1 px-2 py-1 rounded-full border text-xs font-medium ${getColor(score)} ${className}`}>
      <span>{getIcon(score)}</span>
      <span>{label}: {(score * 100).toFixed(0)}%</span>
    </div>
  );
}
