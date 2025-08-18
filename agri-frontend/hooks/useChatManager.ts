import { useState, useCallback, useEffect } from 'react'
import { apiService, ChatSession, ChatMessage } from '../lib/api'

interface ChatManagerState {
  sessions: ChatSession[]
  currentSession: ChatSession | null
  messages: ChatMessage[]
  isLoading: boolean
  error: string | null
}

export function useChatManager() {
  const [state, setState] = useState<ChatManagerState>({
    sessions: [],
    currentSession: null,
    messages: [],
    isLoading: false,
    error: null
  })

  // Load chat sessions
  const loadSessions = useCallback(async () => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }))
      const response = await apiService.getChatSessions()
      setState(prev => ({ 
        ...prev, 
        sessions: response.sessions, 
        isLoading: false 
      }))
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error.message : 'Failed to load sessions',
        isLoading: false 
      }))
    }
  }, [])

  // Create new chat session
  const createSession = useCallback(async (title?: string, languagePreference?: string) => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }))
      
      const newSession = await apiService.createChatSession({
        title: title || 'New Chat',
        language_preference: languagePreference || 'english',
        location_context: {
          timestamp: new Date().toISOString()
        }
      })
      
      setState(prev => ({ 
        ...prev, 
        sessions: [newSession, ...prev.sessions],
        currentSession: newSession,
        messages: [],
        isLoading: false 
      }))
      
      return newSession
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error.message : 'Failed to create session',
        isLoading: false 
      }))
      throw error
    }
  }, [])

  // Select a session and load its messages
  const selectSession = useCallback(async (sessionId: string) => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }))
      
      const [session, messages] = await Promise.all([
        apiService.getChatSession(sessionId),
        apiService.getSessionMessages(sessionId)
      ])
      
      setState(prev => ({ 
        ...prev, 
        currentSession: session,
        messages: messages,
        isLoading: false 
      }))
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error.message : 'Failed to load session',
        isLoading: false 
      }))
    }
  }, [])

  // Send a message (non-streaming)
  const sendMessage = useCallback(async (content: string, sessionId?: string) => {
    const targetSessionId = sessionId || state.currentSession?.id
    if (!targetSessionId) {
      throw new Error('No active session')
    }

    try {
      const messages = await apiService.sendMessage(targetSessionId, content)
      
      setState(prev => ({ 
        ...prev, 
        messages: [...prev.messages, ...messages]
      }))
      
      return messages
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error.message : 'Failed to send message'
      }))
      throw error
    }
  }, [state.currentSession?.id])

  // Add streaming message to state
  const addStreamingMessage = useCallback((userContent: string, streamingResponse: string) => {
    const userMessage: ChatMessage = {
      id: `user_${Date.now()}`,
      session_id: state.currentSession?.id || '',
      role: 'user',
      content: userContent,
      original_language: state.currentSession?.language_preference || 'english',
      translated_content: null,
      created_at: new Date().toISOString(),
      tokens_used: null,
      processing_time: null,
      confidence_score: null,
      detected_topic: null,
      expert_consulted: null,
      tools_used: [],
      fact_check_status: null,
      accuracy_score: null,
      user_feedback: null
    }

    const assistantMessage: ChatMessage = {
      id: `assistant_${Date.now()}`,
      session_id: state.currentSession?.id || '',
      role: 'assistant',
      content: streamingResponse,
      original_language: state.currentSession?.language_preference || 'english',
      translated_content: null,
      created_at: new Date().toISOString(),
      tokens_used: null,
      processing_time: null,
      confidence_score: null,
      detected_topic: null,
      expert_consulted: null,
      tools_used: [],
      fact_check_status: 'approved',
      accuracy_score: null,
      user_feedback: null
    }

    setState(prev => ({ 
      ...prev, 
      messages: [...prev.messages, userMessage, assistantMessage]
    }))
  }, [state.currentSession?.id, state.currentSession?.language_preference])

  // Update session
  const updateSession = useCallback(async (sessionId: string, updates: {
    title?: string
    is_active?: boolean
    satisfaction_rating?: number
  }) => {
    try {
      const updatedSession = await apiService.updateChatSession(sessionId, updates)
      
      setState(prev => ({
        ...prev,
        sessions: prev.sessions.map(s => s.id === sessionId ? updatedSession : s),
        currentSession: prev.currentSession?.id === sessionId ? updatedSession : prev.currentSession
      }))
      
      return updatedSession
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error.message : 'Failed to update session'
      }))
      throw error
    }
  }, [])

  // Delete session
  const deleteSession = useCallback(async (sessionId: string) => {
    try {
      await apiService.deleteChatSession(sessionId)
      
      setState(prev => ({
        ...prev,
        sessions: prev.sessions.filter(s => s.id !== sessionId),
        currentSession: prev.currentSession?.id === sessionId ? null : prev.currentSession,
        messages: prev.currentSession?.id === sessionId ? [] : prev.messages
      }))
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error.message : 'Failed to delete session'
      }))
      throw error
    }
  }, [])

  // Clear error
  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }))
  }, [])

  // Load sessions on mount
  useEffect(() => {
    if (apiService.isAuthenticated()) {
      loadSessions()
    }
  }, [loadSessions])

  return {
    sessions: state.sessions,
    currentSession: state.currentSession,
    messages: state.messages,
    isLoading: state.isLoading,
    error: state.error,
    
    // Actions
    loadSessions,
    createSession,
    selectSession,
    sendMessage,
    addStreamingMessage,
    updateSession,
    deleteSession,
    clearError
  }
}
