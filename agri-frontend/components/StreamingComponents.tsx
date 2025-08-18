import React, { useState, useRef, useEffect } from 'react'

interface StreamingTextProps {
  text: string
  speed?: number
  onComplete?: () => void
  className?: string
}

export function StreamingText({ text, speed = 50, onComplete, className = "" }: StreamingTextProps) {
  const [displayedText, setDisplayedText] = useState("")
  const [isComplete, setIsComplete] = useState(false)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const indexRef = useRef(0)

  useEffect(() => {
    if (!text) return

    setDisplayedText("")
    setIsComplete(false)
    indexRef.current = 0

    intervalRef.current = setInterval(() => {
      if (indexRef.current < text.length) {
        setDisplayedText(text.slice(0, indexRef.current + 1))
        indexRef.current++
      } else {
        if (intervalRef.current) {
          clearInterval(intervalRef.current)
        }
        setIsComplete(true)
        onComplete?.()
      }
    }, speed)

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [text, speed, onComplete])

  return (
    <div className={className}>
      {displayedText}
      {!isComplete && (
        <span className="inline-block w-2 h-5 bg-blue-600 animate-pulse ml-1" />
      )}
    </div>
  )
}

interface ProgressBarProps {
  progress: number
  className?: string
  showPercentage?: boolean
}

export function ProgressBar({ progress, className = "", showPercentage = true }: ProgressBarProps) {
  return (
    <div className={`w-full ${className}`}>
      <div className="flex justify-between text-xs text-gray-600 mb-1">
        <span>Processing...</span>
        {showPercentage && <span>{Math.round(progress)}%</span>}
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full transition-all duration-300 ease-out"
          style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
        />
      </div>
    </div>
  )
}

interface PulsingDotProps {
  color?: string
  size?: 'sm' | 'md' | 'lg'
}

export function PulsingDot({ color = "blue", size = "md" }: PulsingDotProps) {
  const sizeClasses = {
    sm: "w-2 h-2",
    md: "w-3 h-3", 
    lg: "w-4 h-4"
  }

  return (
    <div className={`${sizeClasses[size]} bg-${color}-500 rounded-full animate-pulse`} />
  )
}

interface TypewriterProps {
  text: string
  speed?: number
  className?: string
  cursor?: boolean
}

export function Typewriter({ text, speed = 100, className = "", cursor = true }: TypewriterProps) {
  const [displayText, setDisplayText] = useState("")
  const [showCursor, setShowCursor] = useState(true)

  useEffect(() => {
    let i = 0
    const timer = setInterval(() => {
      if (i < text.length) {
        setDisplayText(text.slice(0, i + 1))
        i++
      } else {
        clearInterval(timer)
        if (cursor) {
          // Keep cursor blinking even after completion
          const cursorTimer = setInterval(() => {
            setShowCursor(prev => !prev)
          }, 500)
          return () => clearInterval(cursorTimer)
        }
      }
    }, speed)

    return () => clearInterval(timer)
  }, [text, speed, cursor])

  return (
    <span className={className}>
      {displayText}
      {cursor && showCursor && (
        <span className="animate-ping">|</span>
      )}
    </span>
  )
}
