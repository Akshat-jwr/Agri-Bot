'use client'

import { useState, useEffect, useRef } from 'react'
import { Send, Loader, AlertCircle, User, Bot, CheckCircle } from 'lucide-react'
import { StreamingText } from '@/components/StreamingText'
import { apiService, ChatMessage } from '@/lib/api'
import { ChatSidebar } from '@/components/ChatSidebar'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [currentMessage, setCurrentMessage] = useState('')
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [authForm, setAuthForm] = useState({ email: '', password: '' })
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login')
  const [authError, setAuthError] = useState('')
  const [isLoadingHistory, setIsLoadingHistory] = useState(false)
  
  // 🔥 SEXY THINKING UI STATES
  const [isThinking, setIsThinking] = useState(false)
  const [thinkingPhase, setThinkingPhase] = useState('')
  const [thinkingProgress, setThinkingProgress] = useState(0)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    setIsAuthenticated(apiService.isAuthenticated())
  }, [])

  // Load chat history when session is created
  const loadChatHistory = async (sessionId: string) => {
    setIsLoadingHistory(true)
    try {
      const chatMessages = await apiService.getSessionMessages(sessionId)
      const formattedMessages: Message[] = chatMessages.map(msg => ({
        id: msg.id,
        role: msg.role as 'user' | 'assistant',
        content: msg.content,
        timestamp: new Date(msg.created_at)
      }))
      setMessages(formattedMessages)
    } catch (error) {
      console.error('Failed to load chat history:', error)
    } finally {
      setIsLoadingHistory(false)
    }
  }

  useEffect(() => {
    setIsAuthenticated(apiService.isAuthenticated())
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault()
    setAuthError('')
    
    try {
      if (authMode === 'login') {
        console.log('🔐 Logging in...')
        await apiService.login(authForm.email, authForm.password)
        setIsAuthenticated(true)
        console.log('✅ Login successful')
        
        // Don't create session immediately - let sendMessage handle it
        // This allows for proper session management with the sidebar
        
      } else {
        await apiService.register(authForm.email, authForm.password)
        alert('Registration successful! Please check your email for verification.')
        setAuthMode('login')
      }
    } catch (error) {
      console.error('❌ Authentication failed:', error)
      setAuthError(error instanceof Error ? error.message : 'Authentication failed')
    }
  }

  // 🔥 SEXY THINKING PHASES
  const thinkingPhases = [
    { title: "🧠 Understanding your query...", duration: 1000 },
    { title: "🌾 Analyzing agricultural data...", duration: 1500 },
    { title: "📊 Processing market insights...", duration: 1200 },
    { title: "🌤️ Checking weather patterns...", duration: 800 },
    { title: "🔬 Consulting research database...", duration: 1300 },
    { title: "💡 Generating intelligent response...", duration: 1000 },
    { title: "✨ Finalizing recommendations...", duration: 700 }
  ]

  const startThinkingAnimation = async () => {
    setIsThinking(true)
    setThinkingProgress(0)
    
    const totalDuration = thinkingPhases.reduce((sum, phase) => sum + phase.duration, 0)
    let currentTime = 0
    
    for (let i = 0; i < thinkingPhases.length; i++) {
      const phase = thinkingPhases[i]
      setThinkingPhase(phase.title)
      
      // Animate progress during this phase
      const startProgress = (currentTime / totalDuration) * 100
      const endProgress = ((currentTime + phase.duration) / totalDuration) * 100
      
      const progressStep = (endProgress - startProgress) / (phase.duration / 50)
      let currentProgress = startProgress
      
      const progressInterval = setInterval(() => {
        currentProgress += progressStep
        setThinkingProgress(Math.min(currentProgress, endProgress))
      }, 50)
      
      await new Promise(resolve => setTimeout(resolve, phase.duration))
      clearInterval(progressInterval)
      currentTime += phase.duration
    }
    
    setThinkingProgress(100)
  }

  const sendMessage = async () => {
    console.log('🚀 Send message clicked')
    console.log('Current message:', currentMessage)
    console.log('Session ID:', sessionId)
    console.log('Is thinking:', isThinking)
    console.log('Is authenticated:', isAuthenticated)
    
    if (!currentMessage.trim()) {
      console.log('❌ Message is empty')
      return
    }
    
    if (isThinking) {
      console.log('❌ Already thinking')
      return
    }
    
    if (!isAuthenticated) {
      console.log('❌ Not authenticated')
      return
    }

    try {
      // Create session if it doesn't exist
      let currentSessionId = sessionId
      if (!currentSessionId) {
        console.log('🔄 Creating new chat session...')
        const session = await apiService.createChatSession({
          title: currentMessage.substring(0, 50) + (currentMessage.length > 50 ? '...' : ''),
          language_preference: 'english'
        })
        currentSessionId = session.id
        setSessionId(currentSessionId)
        console.log('✅ Created session:', currentSessionId)
      }

      const userMessage: Message = {
        id: Date.now().toString(),
        role: 'user',
        content: currentMessage,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, userMessage])
      const messageToSend = currentMessage
      setCurrentMessage('')

      console.log('📤 Sending message to session:', currentSessionId)
      console.log('Message content:', messageToSend)
      
      // Start the sexy thinking animation
      const thinkingPromise = startThinkingAnimation()
      
      // Send message to API
      const responsePromise = apiService.sendMessage(currentSessionId, messageToSend)
      
      // Wait for both to complete
      const [_, responseMessages] = await Promise.all([thinkingPromise, responsePromise])
      
      // Get the assistant's response (should be the last message)
      const assistantResponse = responseMessages.find(msg => msg.role === 'assistant')
      
      if (assistantResponse) {
        // Add the complete response
        const assistantMessage: Message = {
          id: Date.now().toString(),
          role: 'assistant',
          content: assistantResponse.content,
          timestamp: new Date()
        }
        
        setMessages(prev => [...prev, assistantMessage])
      }
      setIsThinking(false)
      console.log('✅ AI processing completed')
      
    } catch (error) {
      console.error('❌ Failed to send message:', error)
      setIsThinking(false)
      
      // Remove the user message if there was an error (find by timestamp since we just added it)
      const currentTime = Date.now()
      setMessages(prev => prev.filter(msg => 
        !(msg.role === 'user' && Math.abs(new Date(msg.timestamp).getTime() - currentTime) < 1000)
      ))
      
      // Add error message to chat
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `**Error**: ${error instanceof Error ? error.message : 'Failed to send message. Please try again.'}`,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
      
      // Restore the message in the input field so user can try again
      setCurrentMessage(currentMessage)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      console.log('⌨️ Enter key pressed')
      sendMessage()
    }
  }

  // Sidebar functions
  const handleSessionSelect = async (selectedSessionId: string) => {
    setSessionId(selectedSessionId)
    setMessages([])
    await loadChatHistory(selectedSessionId)
  }

  const handleNewChat = async () => {
    console.log('🆕 Starting new chat...')
    setSessionId(null)
    setMessages([])
    
    // Session will be created when first message is sent
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-xl p-8 w-full max-w-md">
          <div className="text-center mb-6">
            <h1 className="text-3xl font-bold mb-2 text-gray-700">
              🌾 KrishiMitra AI
            </h1>
            <p className="text-gray-700">Your Agricultural Intelligence Assistant</p>
          </div>

          <form onSubmit={handleAuth} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1 text-gray-700">
                Email
              </label>
              <input
                type="email"
                value={authForm.email}
                onChange={(e) => setAuthForm(prev => ({ ...prev, email: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 text-gray-700"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1 text-gray-700">
                Password
              </label>
              <input
                type="password"
                value={authForm.password}
                onChange={(e) => setAuthForm(prev => ({ ...prev, password: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 text-gray-700"
                required
              />
            </div>

            {authError && (
              <div className="text-sm text-red-600">{authError}</div>
            )}

            <button
              type="submit"
              className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              {authMode === 'login' ? 'Login' : 'Register'}
            </button>

            <div className="text-center">
              <button
                type="button"
                onClick={() => setAuthMode(authMode === 'login' ? 'register' : 'login')}
                className="hover:text-green-700 text-sm text-green-600"
              >
                {authMode === 'login' ? 'Need an account? Register' : 'Have an account? Login'}
              </button>
            </div>
          </form>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-green-50 to-blue-50 flex">
      {/* 🔥 ALWAYS VISIBLE PROFESSIONAL SIDEBAR */}
      <div className="w-80 bg-white border-r border-slate-200 shadow-xl flex flex-col">
        <ChatSidebar
          isOpen={true}
          onToggle={() => {}} // No toggle needed since always open
          currentSessionId={sessionId}
          onSessionSelect={handleSessionSelect}
          onNewChat={handleNewChat}
        />
      </div>

      {/* 🎨 MAIN CHAT AREA - PROFESSIONAL LAYOUT */}
      <div className="flex-1 flex flex-col min-h-screen">
        {/* 💎 PREMIUM HEADER */}
        <header className="bg-white/95 backdrop-blur-sm shadow-sm border-b border-slate-200 sticky top-0 z-10">
          <div className="px-8 py-6 flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-green-600 rounded-xl flex items-center justify-center shadow-lg">
                <span className="text-xl">🌾</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-700">
                  KrishiMitra AI
                </h1>
                <p className="text-sm text-gray-700">Your Agricultural Intelligence Assistant</p>
              </div>
              {isThinking && (
                <div className="flex items-center space-x-3 bg-green-50 px-4 py-2 rounded-full border border-green-200">
                  <Loader className="w-4 h-4 animate-spin text-green-600" />
                  <span className="text-sm text-green-800 font-medium">{thinkingPhase}</span>
                </div>
              )}
            </div>
            
            <div className="flex items-center space-x-4">
              {isLoadingHistory && (
                <div className="flex items-center space-x-2 text-gray-700">
                  <Loader className="w-4 h-4 animate-spin" />
                  <span className="text-sm">Loading history...</span>
                </div>
              )}
              <button
                onClick={() => {
                  apiService.logout()
                  setIsAuthenticated(false)
                  setMessages([])
                  setSessionId(null)
                }}
                className="flex items-center space-x-2 px-4 py-2 text-gray-700 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-all duration-200"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                <span className="text-sm font-medium">Logout</span>
              </button>
            </div>
          </div>
        </header>

        {/*  PREMIUM CHAT MESSAGES AREA */}
        <main className="flex-1 overflow-y-auto bg-gradient-to-b from-slate-50/50 to-white">
          <div className="max-w-4xl mx-auto px-8 py-6">
            {messages.length === 0 ? (
              <div className="text-center py-20">
                <div className="mb-8">
                  <div className="w-20 h-20 bg-gradient-to-r from-green-500 to-green-600 rounded-2xl mx-auto mb-6 flex items-center justify-center shadow-lg">
                    <span className="text-3xl">🌾</span>
                  </div>
                  <h2 className="text-4xl font-bold mb-4 text-gray-700">
                    Welcome to KrishiMitra AI
                  </h2>
                  <p className="text-xl text-gray-700 mb-12 max-w-2xl mx-auto">
                    Your intelligent agricultural assistant powered by advanced AI technology
                  </p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
                  <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                    <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center mb-4">
                      <span className="text-2xl">🌾</span>
                    </div>
                    <h3 className="font-bold text-lg mb-3 text-gray-700">Crop Analysis</h3>
                    <p className="text-gray-700 leading-relaxed">Get detailed insights about crop health, disease detection, and yield optimization strategies</p>
                  </div>
                  
                  <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                    <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-4">
                      <span className="text-2xl">🌤️</span>
                    </div>
                    <h3 className="font-bold text-lg mb-3 text-gray-700">Weather Insights</h3>
                    <p className="text-gray-700 leading-relaxed">Receive weather-based farming recommendations and seasonal planning advice</p>
                  </div>
                  
                  <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                    <div className="w-12 h-12 bg-yellow-100 rounded-xl flex items-center justify-center mb-4">
                      <span className="text-2xl">💰</span>
                    </div>
                    <h3 className="font-bold text-lg mb-3 text-gray-700">Market Intelligence</h3>
                    <p className="text-gray-700 leading-relaxed">Access real-time agricultural market prices and trading information</p>
                  </div>
                  
                  <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                    <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mb-4">
                      <span className="text-2xl">🔬</span>
                    </div>
                    <h3 className="font-bold text-lg mb-3 text-gray-700">Research & Best Practices</h3>
                    <p className="text-gray-700 leading-relaxed">Get evidence-based agricultural research and proven methodologies</p>
                  </div>
                </div>
                
                <div className="mt-12">
                  <p className="text-gray-700 bg-white px-6 py-3 rounded-full inline-block shadow-sm border border-slate-200">
                    💡 Start by asking a question about agriculture, farming, or any crop-related topic!
                  </p>
                </div>
              </div>
            ) : (
              <div className="space-y-8">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`flex items-start space-x-4 max-w-4xl ${
                        message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                      }`}
                    >
                      <div className={`w-10 h-10 rounded-2xl flex items-center justify-center shadow-lg ${
                        message.role === 'user' 
                          ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white' 
                          : 'bg-gradient-to-r from-green-500 to-green-600 text-white'
                      }`}>
                        {message.role === 'user' ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
                      </div>
                      <div
                        className={`rounded-2xl p-6 shadow-lg border max-w-3xl ${
                          message.role === 'user'
                            ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white border-blue-300'
                            : 'bg-white border-slate-200'
                        }`}
                      >
                        {message.role === 'user' ? (
                          <p className="whitespace-pre-wrap text-white leading-relaxed">{message.content}</p>
                        ) : (
                          <div className="text-gray-700 leading-relaxed">
                            <StreamingText 
                              text={message.content || "ERROR: Empty content"} 
                              isStreaming={false}
                            />
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}

                {/* 🔥 PREMIUM THINKING BUBBLE */}
                {isThinking && (
                  <div className="flex justify-start">
                    <div className="flex items-start space-x-4 max-w-4xl">
                      <div className="w-10 h-10 rounded-2xl bg-gradient-to-r from-green-400 to-green-600 text-white flex items-center justify-center shadow-lg animate-pulse">
                        <Bot className="w-5 h-5" />
                      </div>
                      <div className="bg-white border border-slate-200 shadow-xl rounded-2xl p-8 min-h-[100px] max-w-3xl">
                        <div className="flex items-center space-x-4 mb-4">
                          <div className="flex space-x-1">
                            <div className="w-3 h-3 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                            <div className="w-3 h-3 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                            <div className="w-3 h-3 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                          </div>
                          <div className="flex-1">
                            <div className="text-green-800 font-semibold text-base mb-1">🧠 KrishiMitra is analyzing...</div>
                            <div className="text-green-700 text-sm">{thinkingPhase}</div>
                          </div>
                        </div>
                        <div className="w-full bg-slate-200 rounded-full h-2 shadow-inner">
                          <div
                            className="bg-gradient-to-r from-green-400 to-green-600 h-2 rounded-full transition-all duration-300 shadow-sm"
                            style={{ width: `${thinkingProgress}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>
            )}
          </div>
        </main>

        {/* 🎨 PREMIUM INPUT AREA */}
        <div className="bg-white/95 backdrop-blur-sm border-t border-slate-200 shadow-lg sticky bottom-0">
          <div className="max-w-4xl mx-auto px-8 py-6">
            <div className="flex space-x-4 items-end">
              <div className="flex-1">
                <textarea
                  value={currentMessage}
                  onChange={(e) => setCurrentMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask about agriculture, farming, crops, weather, market trends..."
                  className="w-full px-6 py-4 border border-slate-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none text-gray-700 placeholder-gray-500 shadow-sm bg-white/90 backdrop-blur-sm transition-all duration-200"
                  rows={3}
                  disabled={isThinking}
                />
              </div>
              <button
                onClick={(e) => {
                  e.preventDefault()
                  console.log('🎯 Button clicked!')
                  sendMessage()
                }}
                disabled={!currentMessage.trim() || isThinking || !isAuthenticated}
                className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white p-4 rounded-2xl focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center shadow-lg transition-all duration-200 hover:shadow-xl disabled:hover:shadow-lg"
                title={!isAuthenticated ? 'Please login first' : isThinking ? 'Thinking...' : 'Send message'}
              >
                {isThinking ? (
                  <Loader className="w-6 h-6 animate-spin" />
                ) : (
                  <Send className="w-6 h-6" />
                )}
              </button>
            </div>
            
            <div className="mt-4 flex items-center justify-center">
              <p className="text-xs text-gray-700 bg-slate-50 px-4 py-2 rounded-full border border-slate-200">
                💡 Tip: Be specific with your agricultural questions for the best results
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
