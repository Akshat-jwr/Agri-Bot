"use client"

import { useState, useEffect, useRef } from "react"
import { Button } from "../components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { Input } from "../components/ui/input"
import { ScrollArea } from "../components/ui/scroll-area"
import { Avatar, AvatarFallback } from "../components/ui/avatar"
import { Badge } from "../components/ui/badge"
import {
  MessageCircle,
  Send,
  MapPin,
  Sprout,
  CloudRain,
  TrendingUp,
  User,
  Bot,
  Mic,
  MicOff,
  History,
  Settings,
  LogOut,
  Trash2,
  Edit2,
} from "lucide-react"

// Import our streaming components and hooks
import { SourcesCard } from "../components/SourcesCard"
import { AIReasoningCard } from "../components/AIReasoningCard"
import { WebSearchCard } from "../components/WebSearchCard"
import { StreamingText, ProgressBar } from "../components/StreamingComponents"
import { useStreamingChat } from "../hooks/useStreamingChat"
import { useChatManager } from "../hooks/useChatManager"
import { ChatMessage } from "../lib/api"

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

export default function AgriculturalAdvisor() {
  const [inputMessage, setInputMessage] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [userLocation, setUserLocation] = useState<{ state: string; district: string } | null>(null)
  const [isListening, setIsListening] = useState(false)
  const [isAuthenticated, setIsAuthenticated] = useState(true) // Auto-authenticate for demo
  const [showSidebar, setShowSidebar] = useState(false)
  const [expandedSources, setExpandedSources] = useState<Record<string, boolean>>({})
  const [expandedReasoning, setExpandedReasoning] = useState<Record<string, boolean>>({})
  const [expandedWebSearch, setExpandedWebSearch] = useState<Record<string, boolean>>({})
  const [editingSession, setEditingSession] = useState<string | null>(null)
  const [newTitle, setNewTitle] = useState("")
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Initialize chat manager and streaming chat hooks
  const { 
    sessions, 
    currentSession, 
    messages, 
    isLoading: chatLoading, 
    error: chatError,
    createSession,
    selectSession,
    addStreamingMessage,
    updateSession,
    deleteSession,
    clearError
  } = useChatManager()

  // Initialize streaming chat hook
  const { streamingState, startStreaming, stopStreaming } = useStreamingChat()

  // Update streaming message in real-time and refresh session messages
  useEffect(() => {
    if (streamingState.streamingText && !streamingState.isStreaming && currentSession) {
      // Streaming completed, refresh the current session to get the latest messages
      const refreshMessages = async () => {
        try {
          await selectSession(currentSession.id)
        } catch (error) {
          console.error("Failed to refresh messages after streaming:", error)
        }
      }
      
      // Small delay to ensure backend has processed the message
      setTimeout(refreshMessages, 1000)
    }
  }, [streamingState.streamingText, streamingState.isStreaming, currentSession, selectSession])

  // Clear errors after a few seconds
  useEffect(() => {
    if (chatError) {
      const timeout = setTimeout(() => {
        clearError()
      }, 5000)
      return () => clearTimeout(timeout)
    }
  }, [chatError, clearError])

  // Get user location on component mount
  useEffect(() => {
    // Demo authentication - set a token if not present
    if (!localStorage.getItem('auth_token')) {
      localStorage.setItem('auth_token', 'demo_user_token_' + Date.now())
    }

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          // In a real app, you'd reverse geocode to get state/district
          // For demo, we'll use placeholder data
          setUserLocation({ state: "Punjab", district: "Ludhiana" })
        },
        (error) => {
          console.log("Location access denied, using fallback")
          setUserLocation({ state: "India", district: "All Districts" })
        },
      )
    } else {
      setUserLocation({ state: "India", district: "All Districts" })
    }
  }, [])

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading || streamingState.isStreaming) return

    // Make sure we have a session
    let sessionId = currentSession?.id
    if (!sessionId) {
      try {
        const newSession = await createSession("New Chat", "english")
        sessionId = newSession.id
      } catch (error) {
        console.error("Failed to create session:", error)
        return
      }
    }

    const messageToSend = inputMessage
    setInputMessage("")
    setIsLoading(true)

    try {
      // Start streaming response
      const token = localStorage.getItem("auth_token") || "demo_token"
      
      await startStreaming(sessionId, messageToSend, token)

    } catch (error) {
      console.error("Error sending message:", error)
      // Handle error appropriately
    } finally {
      setIsLoading(false)
    }
  }

  const handleNewChat = async () => {
    try {
      await createSession("New Chat", "english")
    } catch (error) {
      console.error("Failed to create new chat:", error)
    }
  }

  const handleSessionSelect = async (sessionId: string) => {
    try {
      await selectSession(sessionId)
      setShowSidebar(false) // Close sidebar on mobile
    } catch (error) {
      console.error("Failed to select session:", error)
    }
  }

  const handleUpdateSessionTitle = async (sessionId: string, title: string) => {
    try {
      await updateSession(sessionId, { title })
      setEditingSession(null)
      setNewTitle("")
    } catch (error) {
      console.error("Failed to update session:", error)
    }
  }

  const handleDeleteSession = async (sessionId: string) => {
    if (confirm("Are you sure you want to delete this chat?")) {
      try {
        await deleteSession(sessionId)
      } catch (error) {
        console.error("Failed to delete session:", error)
      }
    }
  }

  const toggleVoiceInput = () => {
    setIsListening(!isListening)
    // In a real app, implement Web Speech API here
  }

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <div
        className={`${showSidebar ? "translate-x-0" : "-translate-x-full"} fixed inset-y-0 left-0 z-50 w-64 bg-sidebar border-r border-sidebar-border transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0`}
      >
        <div className="flex flex-col h-full">
          <div className="p-4 border-b border-sidebar-border">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-sidebar-primary rounded-full flex items-center justify-center">
                <Sprout className="w-4 h-4 text-sidebar-primary-foreground" />
              </div>
              <span className="font-bold text-sidebar-foreground">KrishiMitra</span>
            </div>
          </div>

          <div className="p-4">
            <Button onClick={handleNewChat} className="w-full mb-4" disabled={chatLoading}>
              <MessageCircle className="w-4 h-4 mr-2" />
              New Chat
            </Button>

            {chatError && (
              <div className="mb-4 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-800">
                {chatError}
              </div>
            )}

            {userLocation && (
              <Card className="mb-4">
                <CardContent className="p-3">
                  <div className="flex items-center gap-2 text-sm">
                    <MapPin className="w-4 h-4 text-primary" />
                    <div>
                      <p className="font-medium">{userLocation.district}</p>
                      <p className="text-muted-foreground">{userLocation.state}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          <ScrollArea className="flex-1 px-4">
            <div className="space-y-2">
              <h3 className="text-sm font-medium text-sidebar-foreground mb-2">Recent Chats</h3>
              {sessions.map((session) => (
                <div key={session.id} className="group relative">
                  <Button
                    variant={currentSession?.id === session.id ? "secondary" : "ghost"}
                    className="w-full justify-start text-left h-auto p-2 pr-8"
                    onClick={() => handleSessionSelect(session.id)}
                  >
                    <div className="truncate">
                      {editingSession === session.id ? (
                        <Input
                          value={newTitle}
                          onChange={(e) => setNewTitle(e.target.value)}
                          onBlur={() => {
                            if (newTitle.trim()) {
                              handleUpdateSessionTitle(session.id, newTitle)
                            } else {
                              setEditingSession(null)
                              setNewTitle("")
                            }
                          }}
                          onKeyPress={(e) => {
                            if (e.key === "Enter") {
                              if (newTitle.trim()) {
                                handleUpdateSessionTitle(session.id, newTitle)
                              } else {
                                setEditingSession(null)
                                setNewTitle("")
                              }
                            }
                          }}
                          className="text-sm h-6 px-1"
                          autoFocus
                        />
                      ) : (
                        <>
                          <p className="text-sm font-medium truncate">{session.title}</p>
                          <p className="text-xs text-muted-foreground">
                            {session.message_count} messages • {new Date(session.created_at).toLocaleDateString()}
                          </p>
                        </>
                      )}
                    </div>
                  </Button>
                  
                  {/* Session controls */}
                  <div className="absolute right-1 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-6 w-6 p-0"
                      onClick={(e) => {
                        e.stopPropagation()
                        setEditingSession(session.id)
                        setNewTitle(session.title)
                      }}
                    >
                      <Edit2 className="w-3 h-3" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-6 w-6 p-0 text-red-500 hover:text-red-700"
                      onClick={(e) => {
                        e.stopPropagation()
                        handleDeleteSession(session.id)
                      }}
                    >
                      <Trash2 className="w-3 h-3" />
                    </Button>
                  </div>
                </div>
              ))}
              
              {sessions.length === 0 && !chatLoading && (
                <p className="text-xs text-muted-foreground text-center py-4">
                  No chat sessions yet. Start a new conversation!
                </p>
              )}
            </div>
          </ScrollArea>

          <div className="p-4 border-t border-sidebar-border">
            <div className="space-y-2">
              <Button variant="ghost" className="w-full justify-start">
                <Settings className="w-4 h-4 mr-2" />
                Settings
              </Button>
              <Button
                variant="ghost"
                className="w-full justify-start"
                onClick={() => {
                  localStorage.removeItem("auth_token")
                  setIsAuthenticated(false)
                }}
              >
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-card border-b border-border p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" className="lg:hidden" onClick={() => setShowSidebar(!showSidebar)}>
                <History className="w-4 h-4" />
              </Button>
              <div>
                <h1 className="text-xl font-bold text-primary">Agricultural AI Advisor</h1>
                <p className="text-sm text-muted-foreground">
                  Ask me anything about farming, crops, weather, and market prices
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="secondary" className="hidden sm:flex">
                <CloudRain className="w-3 h-3 mr-1" />
                Weather: 28°C
              </Badge>
              <Badge variant="outline" className="hidden sm:flex">
                <TrendingUp className="w-3 h-3 mr-1" />
                Market: Active
              </Badge>
            </div>
          </div>
        </div>

        {/* Messages */}
        <ScrollArea className="flex-1 p-4">
          <div className="max-w-4xl mx-auto space-y-4">
            {messages.length === 0 ? (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Sprout className="w-8 h-8 text-primary" />
                </div>
                <h2 className="text-xl font-semibold mb-2">Welcome to KrishiMitra!</h2>
                <p className="text-muted-foreground mb-6">
                  Your AI-powered agricultural advisor. Ask me about crops, weather, market prices, or farming
                  techniques.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
                  <Card
                    className="cursor-pointer hover:bg-accent/5 transition-colors"
                    onClick={() => setInputMessage("What crops should I plant this season?")}
                  >
                    <CardContent className="p-4">
                      <h3 className="font-medium mb-1">Crop Recommendations</h3>
                      <p className="text-sm text-muted-foreground">Get personalized crop suggestions</p>
                    </CardContent>
                  </Card>
                  <Card
                    className="cursor-pointer hover:bg-accent/5 transition-colors"
                    onClick={() => setInputMessage("What are the current market prices?")}
                  >
                    <CardContent className="p-4">
                      <h3 className="font-medium mb-1">Market Prices</h3>
                      <p className="text-sm text-muted-foreground">Check latest mandi rates</p>
                    </CardContent>
                  </Card>
                  <Card
                    className="cursor-pointer hover:bg-accent/5 transition-colors"
                    onClick={() => setInputMessage("How's the weather looking for farming?")}
                  >
                    <CardContent className="p-4">
                      <h3 className="font-medium mb-1">Weather Forecast</h3>
                      <p className="text-sm text-muted-foreground">Get farming-focused weather updates</p>
                    </CardContent>
                  </Card>
                  <Card
                    className="cursor-pointer hover:bg-accent/5 transition-colors"
                    onClick={() => setInputMessage("Help me with pest control")}
                  >
                    <CardContent className="p-4">
                      <h3 className="font-medium mb-1">Pest Management</h3>
                      <p className="text-sm text-muted-foreground">Learn about pest prevention</p>
                    </CardContent>
                  </Card>
                </div>
              </div>
            ) : (
              messages.map((message) => {
                // Convert ChatMessage to display format
                const displayMessage = {
                  id: message.id,
                  role: message.role,
                  content: message.content,
                  timestamp: new Date(message.created_at),
                  confidence_score: message.confidence_score,
                  detected_topic: message.detected_topic,
                  tools_used: message.tools_used,
                  fact_check_status: message.fact_check_status,
                  accuracy_score: message.accuracy_score
                }

                return (
                  <div
                    key={message.id}
                    className={`flex gap-3 ${message.role === "user" ? "justify-end" : "justify-start"}`}
                  >
                    {message.role === "assistant" && (
                      <Avatar className="w-8 h-8 bg-primary">
                        <AvatarFallback>
                          <Bot className="w-4 h-4 text-primary-foreground" />
                        </AvatarFallback>
                      </Avatar>
                    )}
                    <div className={`max-w-[80%] ${message.role === "user" ? "order-first" : ""}`}>
                      <Card className={message.role === "user" ? "bg-primary text-primary-foreground" : "bg-card"}>
                        <CardContent className="p-3">
                          {/* Check if this is the streaming message */}
                          {message.role === "assistant" && 
                           message.id === messages[messages.length - 1]?.id && 
                           streamingState.isStreaming ? (
                            <>
                              {/* Live Progress Bar */}
                              {streamingState.progress > 0 && (
                                <ProgressBar 
                                  progress={streamingState.progress} 
                                  className="mb-3"
                                  showPercentage={true}
                                />
                              )}

                              {/* Current Phase Display */}
                              {streamingState.phaseTitle && (
                                <div className="mb-3 p-2 bg-blue-50 rounded-lg border-l-4 border-blue-500">
                                  <div className="flex items-center gap-2">
                                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
                                    <span className="text-sm font-medium text-blue-800">
                                      {streamingState.phaseTitle}
                                    </span>
                                  </div>
                                </div>
                              )}

                              {/* Streaming Text Response */}
                              {streamingState.streamingText && (
                                <StreamingText 
                                  text={streamingState.streamingText}
                                  speed={30}
                                  className="text-sm whitespace-pre-wrap"
                                />
                              )}

                              {/* Error Display */}
                              {streamingState.error && (
                                <div className="p-2 bg-red-50 border border-red-200 rounded-lg">
                                  <p className="text-sm text-red-800">❌ {streamingState.error}</p>
                                </div>
                              )}
                            </>
                          ) : (
                            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                          )}

                          {/* Sources Card - Only show if streaming and has sources or if message is complete */}
                          {streamingState.sources.length > 0 && message.role === "assistant" && (
                            <SourcesCard
                              sources={streamingState.sources}
                              isExpanded={expandedSources[message.id] || false}
                              onToggle={() => setExpandedSources(prev => ({
                                ...prev,
                                [message.id]: !prev[message.id]
                              }))}
                            />
                          )}

                          {/* AI Reasoning Card */}
                          {streamingState.reasoningSteps.length > 0 && message.role === "assistant" && (
                            <AIReasoningCard
                              steps={streamingState.reasoningSteps}
                              isExpanded={expandedReasoning[message.id] || false}
                              onToggle={() => setExpandedReasoning(prev => ({
                                ...prev,
                                [message.id]: !prev[message.id]
                              }))}
                              isProcessing={streamingState.isStreaming && streamingState.currentPhase === 'ai_reasoning'}
                            />
                          )}

                          {/* Web Search Card */}
                          {streamingState.webSearchQueries.length > 0 && message.role === "assistant" && (
                            <WebSearchCard
                              queries={streamingState.webSearchQueries}
                              isExpanded={expandedWebSearch[message.id] || false}
                              onToggle={() => setExpandedWebSearch(prev => ({
                                ...prev,
                                [message.id]: !prev[message.id]
                              }))}
                              isSearching={streamingState.isStreaming && streamingState.currentPhase === 'web_search'}
                            />
                          )}

                          {/* Message metadata for assistant messages */}
                          {message.role === "assistant" && !(streamingState.isStreaming && message.id === messages[messages.length - 1]?.id) && (
                            <div className="mt-2 pt-2 border-t border-border/20">
                              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                {displayMessage.confidence_score && (
                                  <Badge variant="secondary" className="text-xs">
                                    {Math.round(displayMessage.confidence_score * 100)}% confident
                                  </Badge>
                                )}
                                {displayMessage.detected_topic && (
                                  <Badge variant="outline" className="text-xs">
                                    {displayMessage.detected_topic.replace("_", " ")}
                                  </Badge>
                                )}
                                {message.fact_check_status && (
                                  <Badge 
                                    variant={message.fact_check_status === 'approved' ? 'secondary' : 'destructive'} 
                                    className="text-xs"
                                  >
                                    ✅ Fact-checked
                                  </Badge>
                                )}
                              </div>
                            </div>
                          )}
                        </CardContent>
                      </Card>
                      <p className="text-xs text-muted-foreground mt-1 px-1">
                        {displayMessage.timestamp.toLocaleTimeString()}
                      </p>
                    </div>
                    {message.role === "user" && (
                      <Avatar className="w-8 h-8 bg-accent">
                        <AvatarFallback>
                          <User className="w-4 h-4 text-accent-foreground" />
                        </AvatarFallback>
                      </Avatar>
                    )}
                  </div>
                )
              })
            )}
            {(isLoading || streamingState.isStreaming) && (
              <div className="flex gap-3 justify-start">
                <Avatar className="w-8 h-8 bg-primary">
                  <AvatarFallback>
                    <Bot className="w-4 h-4 text-primary-foreground" />
                  </AvatarFallback>
                </Avatar>
                <Card className="bg-card max-w-[80%]">
                  <CardContent className="p-3">
                    {streamingState.isStreaming ? (
                      <div className="space-y-2">
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-primary rounded-full animate-bounce"></div>
                          <div
                            className="w-2 h-2 bg-primary rounded-full animate-bounce"
                            style={{ animationDelay: "0.1s" }}
                          ></div>
                          <div
                            className="w-2 h-2 bg-primary rounded-full animate-bounce"
                            style={{ animationDelay: "0.2s" }}
                          ></div>
                          <span className="text-sm text-muted-foreground ml-2">
                            {streamingState.phaseTitle || "Analyzing your agricultural query..."}
                          </span>
                        </div>
                        {streamingState.progress > 0 && (
                          <ProgressBar 
                            progress={streamingState.progress} 
                            showPercentage={true}
                          />
                        )}
                      </div>
                    ) : (
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-primary rounded-full animate-bounce"></div>
                        <div
                          className="w-2 h-2 bg-primary rounded-full animate-bounce"
                          style={{ animationDelay: "0.1s" }}
                        ></div>
                        <div
                          className="w-2 h-2 bg-primary rounded-full animate-bounce"
                          style={{ animationDelay: "0.2s" }}
                        ></div>
                        <span className="text-sm text-muted-foreground ml-2">Analyzing your query...</span>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>

        {/* Input Area */}
        <div className="border-t border-border p-4">
          <div className="max-w-4xl mx-auto">
            <div className="flex gap-2">
              <div className="flex-1 relative">
                <Input
                  value={inputMessage}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setInputMessage(e.target.value)}
                  placeholder="Ask about crops, weather, market prices, or farming techniques..."
                  onKeyPress={(e: React.KeyboardEvent<HTMLInputElement>) => e.key === "Enter" && handleSendMessage()}
                  className="pr-12"
                  disabled={streamingState.isStreaming || chatLoading}
                />
                <Button
                  size="sm"
                  variant="ghost"
                  className="absolute right-1 top-1/2 -translate-y-1/2"
                  onClick={toggleVoiceInput}
                  disabled={streamingState.isStreaming || chatLoading}
                >
                  {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                </Button>
              </div>
              <Button 
                onClick={handleSendMessage} 
                disabled={!inputMessage.trim() || isLoading || streamingState.isStreaming || chatLoading}
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>
            <p className="text-xs text-muted-foreground mt-2 text-center">
              KrishiMitra provides real-time AI responses with live fact-checking. Please verify important agricultural decisions.
            </p>
          </div>
        </div>
      </div>

      {/* Overlay for mobile sidebar */}
      {showSidebar && (
        <div className="fixed inset-0 bg-black/50 z-40 lg:hidden" onClick={() => setShowSidebar(false)} />
      )}
    </div>
  )
}
