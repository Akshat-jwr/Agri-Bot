'use client'

import { useState, useEffect } from 'react'
import { MarkdownRenderer } from './MarkdownRenderer'

interface StreamingTextProps {
  text: string
  isStreaming: boolean
  className?: string
}

export function StreamingText({ text, isStreaming, className = '' }: StreamingTextProps) {
  const [displayedText, setDisplayedText] = useState('')
  const [currentIndex, setCurrentIndex] = useState(0)

  useEffect(() => {
    if (!isStreaming) {
      setDisplayedText(text)
      setCurrentIndex(text.length)
      return
    }

    if (currentIndex < text.length) {
      const timer = setTimeout(() => {
        setDisplayedText(text.slice(0, currentIndex + 1))
        setCurrentIndex(currentIndex + 1)
      }, 20) // Typing speed

      return () => clearTimeout(timer)
    }
  }, [text, currentIndex, isStreaming])

  useEffect(() => {
    if (isStreaming) {
      setCurrentIndex(0)
      setDisplayedText('')
    } else {
      setDisplayedText(text)
      setCurrentIndex(text.length)
    }
  }, [text, isStreaming])

  return (
    <div className={className}>
      <MarkdownRenderer content={displayedText || text} />
      {isStreaming && (
        <span className="inline-block w-2 h-5 bg-green-500 animate-pulse ml-1" />
      )}
    </div>
  )
}
