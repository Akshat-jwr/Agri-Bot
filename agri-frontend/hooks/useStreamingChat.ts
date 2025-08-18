import { useState, useCallback, useRef, useEffect } from 'react'

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
  error: string | null
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
    error: null
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
        error: null
      })

      // Create EventSource for streaming
      const eventSource = new EventSource(
        `http://localhost:8000/api/v1/streaming/chat?session_id=${sessionId}&content=${encodeURIComponent(content)}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        } as any
      )

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
                newState.streamingText = data.chunk || ''
                newState.progress = data.progress || prev.progress
                break

              case 'fact_check_result':
                newState.factCheckStatus = data.status || ''
                break

              case 'completion':
                newState.isStreaming = false
                newState.progress = 100
                // Mark all reasoning steps as completed
                newState.reasoningSteps = prev.reasoningSteps.map(step => ({
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
