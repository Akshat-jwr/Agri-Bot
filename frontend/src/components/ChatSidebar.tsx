'use client'

import { useState, useEffect } from 'react'
import { apiService, ChatSession } from '@/lib/api'
import { MessageCircle, Plus, Trash2, Calendar, Hash, X, Menu } from 'lucide-react'

interface ChatSidebarProps {
  isOpen: boolean
  onToggle: () => void
  currentSessionId: string | null
  onSessionSelect: (sessionId: string) => void
  onNewChat: () => void
  refreshKey?: number // triggers reload when incremented
}

export function ChatSidebar({ 
  isOpen, 
  onToggle, 
  currentSessionId, 
  onSessionSelect, 
  onNewChat,
  refreshKey
}: ChatSidebarProps) {
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (isOpen) {
      loadSessions()
    }
  }, [isOpen, refreshKey])

  const loadSessions = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await apiService.getChatSessions(1, 50)
      setSessions(response.sessions || [])
    } catch (err) {
      console.error('Failed to load chat sessions:', err)
      setError('Failed to load chat sessions')
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteSession = async (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation()

    try {
      await apiService.deleteChatSession(sessionId)
      setSessions(sessions.filter(s => s.id !== sessionId))
      if (currentSessionId === sessionId) {
        onNewChat()
      }
    } catch (err) {
      console.error('Failed to delete session:', err)
      alert('Failed to delete chat session')
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffTime = now.getTime() - date.getTime()
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))

    if (diffDays === 0) {
      return 'Today'
    } else if (diffDays === 1) {
      return 'Yesterday'
    } else if (diffDays < 7) {
      return `${diffDays} days ago`
    } else {
      return date.toLocaleDateString()
    }
  }

  const truncateTitle = (title: string, maxLength: number = 30) => {
    if (title.length <= maxLength) return title
    return title.substring(0, maxLength) + '...'
  }

  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onToggle}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed top-0 left-0 h-full bg-white border-r border-green-200 shadow-lg z-50 transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        w-80 lg:w-80
      `}>
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-green-200 bg-green-50">
          <h2 className="text-lg font-semibold" style={{ color: '#166534' }}>
            Chat History
          </h2>
          <div className="flex items-center space-x-2">
            <button
              onClick={onNewChat}
              className="p-2 text-green-600 hover:bg-green-100 rounded-lg transition-colors"
              title="New Chat"
            >
              <Plus className="w-5 h-5" />
            </button>
            <button
              onClick={onToggle}
              className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg transition-colors lg:hidden"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Sessions List */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center p-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500"></div>
              <span className="ml-3" style={{ color: '#4b5563' }}>Loading sessions...</span>
            </div>
          ) : error ? (
            <div className="p-4 text-center">
              <p className="text-red-600 mb-2">{error}</p>
              <button
                onClick={loadSessions}
                className="text-green-600 hover:text-green-700 underline"
              >
                Try again
              </button>
            </div>
          ) : sessions.length === 0 ? (
            <div className="p-6 text-center">
              <MessageCircle className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500 mb-4">No chat sessions yet</p>
              <button
                onClick={onNewChat}
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
              >
                Start your first chat
              </button>
            </div>
          ) : (
            <div className="divide-y divide-gray-100">
              {sessions.map((session) => (
                <div
                  key={session.id}
                  onClick={() => onSessionSelect(session.id)}
                  className={`
                    p-4 cursor-pointer transition-colors hover:bg-green-50 group
                    ${currentSessionId === session.id ? 'bg-green-100 border-r-4 border-green-500' : ''}
                  `}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h3 
                        className="font-medium text-sm mb-1 line-clamp-2"
                        style={{ color: '#1f2937' }}
                        title={session.title}
                      >
                        {truncateTitle(session.title || 'Untitled Chat')}
                      </h3>
                      
                      <div className="flex items-center space-x-2 text-xs" style={{ color: '#6b7280' }}>
                        <Calendar className="w-3 h-3" />
                        <span>{formatDate(session.created_at)}</span>
                      </div>
                      
                      <div className="flex items-center space-x-4 mt-2 text-xs" style={{ color: '#6b7280' }}>
                        <div className="flex items-center space-x-1">
                          <Hash className="w-3 h-3" />
                          <span>{session.message_count} messages</span>
                        </div>
                        
                        {session.primary_topic && (
                          <span className="bg-green-100 text-green-700 px-2 py-0.5 rounded text-xs">
                            {session.primary_topic}
                          </span>
                        )}
                      </div>
                    </div>
                    
                    <button
                      onClick={(e) => handleDeleteSession(session.id, e)}
                      className="opacity-0 group-hover:opacity-100 p-1 text-red-500 hover:bg-red-50 rounded transition-all"
                      title="Delete chat"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-green-200 bg-gray-50">
          <p className="text-xs text-center" style={{ color: '#6b7280' }}>
            🌾 AgriMitra AI - Your farming assistant
          </p>
        </div>
      </div>

      {/* Toggle Button (when sidebar is closed) */}
      {!isOpen && (
        <button
          onClick={onToggle}
          className="fixed top-4 left-4 z-40 p-3 bg-green-600 text-white rounded-lg shadow-lg hover:bg-green-700 transition-colors lg:hidden"
        >
          <Menu className="w-5 h-5" />
        </button>
      )}
    </>
  )
}
