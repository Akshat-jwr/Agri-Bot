'use client'

import { useState, useCallback, useRef } from 'react'
import { apiService } from '@/lib/api'

export interface StreamingState {
  isStreaming: boolean
  progress: number
  currentPhase: string
  phaseTitle: string
  streamingText: string
  factCheckStatus: string
  error: string | null
  confidence: number
  validationStatus: string
  sources: Array<{
    title: string
    url: string
    snippet: string
    confidence: number
  }>
  reasoningSteps: Array<{
    step: string
    detail: string
    status: 'processing' | 'complete'
  }>
}

export function useStreamingChat() {
  const [streamingState, setStreamingState] = useState<StreamingState>({
    isStreaming: false,
    progress: 0,
    currentPhase: '',
    phaseTitle: '',
    streamingText: '',
    factCheckStatus: '',
    error: null,
    confidence: 0,
    validationStatus: '',
    sources: [],
    reasoningSteps: []
  })

  const eventSourceRef = useRef<EventSource | null>(null)

  const startStreaming = useCallback(async (sessionId: string, content: string) => {
    console.log('🚀 Starting AI processing...')
    
    try {
      // Reset state and show loading immediately with the box
      setStreamingState({
        isStreaming: true,
        progress: 5,
        currentPhase: 'initializing',
        phaseTitle: 'Initializing AI system...',
        streamingText: '', // Start with empty text but box is visible
        factCheckStatus: '',
        error: null,
        confidence: 0,
        validationStatus: '',
        sources: [],
        reasoningSteps: []
      })

      const token = localStorage.getItem('auth_token')
      if (!token) {
        throw new Error('No authentication token found')
      }

      // Show progress updates with delays to make it smooth
      await new Promise(resolve => setTimeout(resolve, 300))
      setStreamingState(prev => ({ ...prev, progress: 15, phaseTitle: 'Connecting to agricultural AI...' }))
      
      await new Promise(resolve => setTimeout(resolve, 400))
      setStreamingState(prev => ({ ...prev, progress: 30, phaseTitle: 'Analyzing your query...' }))
      
      await new Promise(resolve => setTimeout(resolve, 300))
      setStreamingState(prev => ({ ...prev, progress: 45, phaseTitle: 'Searching knowledge base...' }))
      
      await new Promise(resolve => setTimeout(resolve, 400))
      setStreamingState(prev => ({ ...prev, progress: 60, phaseTitle: 'Generating response...' }))

      // Use regular API call instead of streaming
      console.log('📤 Sending message via API...')
      const response = await apiService.sendMessage(sessionId, content)
      
      console.log('✅ Received response:', response)
      
      if (response && response.length > 0) {
        const aiMessage = response.find(msg => msg.role === 'assistant')
        if (aiMessage) {
          // Start showing the response with a nice transition
          setStreamingState(prev => ({ 
            ...prev, 
            progress: 75, 
            phaseTitle: 'Delivering response...',
            currentPhase: 'response'
          }))

          await new Promise(resolve => setTimeout(resolve, 200))

          // Simulate streaming effect by showing text gradually
          const fullText = aiMessage.content
          const words = fullText.split(' ')
          let currentText = ''
          
          // Stream text word by word for nice effect
          for (let i = 0; i < words.length; i++) {
            currentText += (i > 0 ? ' ' : '') + words[i]
            setStreamingState(prev => ({ 
              ...prev, 
              streamingText: currentText,
              progress: 75 + ((i + 1) / words.length) * 20
            }))
            
            // Variable delay for more natural streaming
            const delay = words[i].length > 8 ? 80 : 60
            if (i < words.length - 1) {
              await new Promise(resolve => setTimeout(resolve, delay))
            }
          }

          // Small final delay before completion
          await new Promise(resolve => setTimeout(resolve, 300))

          // Complete - but keep streaming for a bit longer to prevent flickering
          setStreamingState(prev => ({
            ...prev,
            progress: 100,
            phaseTitle: 'Complete!',
            confidence: aiMessage.confidence_score || 0.9,
            validationStatus: aiMessage.fact_check_status || 'approved'
          }))

          // End streaming after a small delay to ensure smooth transition
          setTimeout(() => {
            setStreamingState(prev => ({
              ...prev,
              isStreaming: false
            }))
          }, 200)
        } else {
          throw new Error('No AI response found')
        }
      } else {
        throw new Error('Empty response received')
      }

    } catch (error) {
      console.error('❌ Failed to process message:', error)
      setStreamingState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Failed to process your request',
        isStreaming: false,
        progress: 0,
        streamingText: '' // Clear any partial text on error
      }))
    }
  }, [])

  const stopStreaming = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
    }
    setStreamingState(prev => ({
      ...prev,
      isStreaming: false
    }))
  }, [])

  return {
    streamingState,
    startStreaming,
    stopStreaming
  }
}
