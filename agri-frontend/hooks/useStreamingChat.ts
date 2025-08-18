import { useState, useCallback, useRef, useEffect } from 'react'
import { apiService } from '../lib/api'

interface StreamingMessage {
  type: string
  message?: string
  progress?: number
  phase?: string
  title?: string
  status?: string
  result?: string
  sources?: any[]
  step?: string
  index?: number
  chunk?: string
  query?: string
  response_id?: string
  confidence?: number
  validation_status?: string
  language?: string
  sources_used?: string[]
  fact_checker_used?: boolean
}

interface Source {
  id: number
  title: string
  type: string
  confidence: number
  url: string
}

interface ReasoningStep {
  step: string
  index: number
  completed?: boolean
}

interface WebSearchQuery {
  query: string
  timestamp: Date
  results?: number
}

interface FactCheckStep {
  step: string
  status: string
  completed?: boolean
}

interface StreamingState {
  isStreaming: boolean
  progress: number
  currentPhase: string
  phaseTitle: string
  sources: Source[]
  reasoningSteps: ReasoningStep[]
  webSearchQueries: WebSearchQuery[]
  streamingText: string
  factCheckStatus: string
  factCheckSteps: FactCheckStep[]
  factCheckCorrections: string
  error: string | null
  confidence: number
  validationStatus: string
  language: string
  sourcesUsed: string[]
  factCheckerUsed: boolean
}

export function useStreamingChat() {
  const [streamingState, setStreamingState] = useState<StreamingState>({
    isStreaming: false,
    progress: 0,
    currentPhase: '',
    phaseTitle: '',
    sources: [],
    reasoningSteps: [],
    webSearchQueries: [],
    streamingText: '',
    factCheckStatus: '',
    factCheckSteps: [],
    factCheckCorrections: '',
    error: null,
    confidence: 0,
    validationStatus: '',
    language: '',
    sourcesUsed: [],
    factCheckerUsed: false
  })

  const eventSourceRef = useRef<EventSource | null>(null)

  const startStreaming = useCallback(async (sessionId: string, content: string, token: string) => {
    try {
      // Reset state
      setStreamingState({
        isStreaming: true,
        progress: 0,
        currentPhase: '',
        phaseTitle: '',
        sources: [],
        reasoningSteps: [],
        webSearchQueries: [],
        streamingText: '',
        factCheckStatus: '',
        factCheckSteps: [],
        factCheckCorrections: '',
        error: null,
        confidence: 0,
        validationStatus: '',
        language: '',
        sourcesUsed: [],
        factCheckerUsed: false
      })

      // Create EventSource using the API service
      const eventSource = apiService.createStreamingEventSource(sessionId, content)
      eventSourceRef.current = eventSource

      eventSource.onmessage = (event) => {
        try {
          const data: StreamingMessage = JSON.parse(event.data)
          
          setStreamingState(prev => {
            const newState = { ...prev }

            switch (data.type) {
              case 'status':
                newState.progress = data.progress || 0
                break

              case 'phase':
                newState.currentPhase = data.phase || ''
                newState.phaseTitle = data.title || ''
                break

              case 'phase_complete':
                newState.progress = data.progress || prev.progress
                break

              case 'sources_found':
                newState.sources = data.sources || []
                newState.progress = data.progress || prev.progress
                break

              case 'ai_step':
                // Handle AI processing steps
                newState.phaseTitle = data.step || newState.phaseTitle
                break

              case 'reasoning_step':
                if (data.step && typeof data.index === 'number') {
                  const newSteps = [...prev.reasoningSteps]
                  newSteps[data.index] = {
                    step: data.step,
                    index: data.index,
                    completed: false
                  }
                  newState.reasoningSteps = newSteps
                }
                break

              case 'fact_check_step':
                if (data.step && data.status) {
                  newState.factCheckSteps = [
                    ...prev.factCheckSteps,
                    {
                      step: data.step,
                      status: data.status,
                      completed: data.status === 'completed'
                    }
                  ]
                }
                break

              case 'web_search_query':
                if (data.query) {
                  newState.webSearchQueries = [
                    ...prev.webSearchQueries,
                    {
                      query: data.query,
                      timestamp: new Date()
                    }
                  ]
                }
                break

              case 'response_start':
                newState.streamingText = ''
                break

              case 'response_chunk':
                // Accumulate chunks to build the full response
                newState.streamingText = data.chunk || ''
                newState.progress = data.progress || prev.progress
                break

              case 'fact_check_result':
                newState.factCheckStatus = data.status || ''
                newState.confidence = data.confidence || 0
                break

              case 'completion':
                newState.isStreaming = false
                newState.progress = 100
                newState.confidence = data.confidence || prev.confidence
                newState.validationStatus = data.validation_status || ''
                newState.language = data.language || ''
                newState.sourcesUsed = data.sources_used || []
                newState.factCheckerUsed = data.fact_checker_used || false
                
                // Mark all steps as completed
                newState.reasoningSteps = prev.reasoningSteps.map(step => ({
                  ...step,
                  completed: true
                }))
                newState.factCheckSteps = prev.factCheckSteps.map(step => ({
                  ...step,
                  completed: true
                }))
                break

              case 'error':
                newState.error = data.message || 'An error occurred'
                newState.isStreaming = false
                break
            }

            return newState
          })
        } catch (error) {
          console.error('Error parsing streaming data:', error)
          setStreamingState(prev => ({
            ...prev,
            error: 'Failed to parse response data',
            isStreaming: false
          }))
        }
      }

      eventSource.onerror = (error) => {
        console.error('EventSource error:', error)
        setStreamingState(prev => ({
          ...prev,
          error: 'Connection error occurred',
          isStreaming: false
        }))
        eventSource.close()
      }

      eventSource.onopen = () => {
        console.log('EventSource connection opened')
      }

    } catch (error) {
      console.error('Error starting stream:', error)
      setStreamingState(prev => ({
        ...prev,
        error: 'Failed to start streaming',
        isStreaming: false
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

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
      }
    }
  }, [])

  return {
    streamingState,
    startStreaming,
    stopStreaming
  }
}
