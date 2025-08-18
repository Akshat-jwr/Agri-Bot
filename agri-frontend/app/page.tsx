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
} from "lucide-react"

// Import our streaming components
import { SourcesCard } from "../components/SourcesCard"
import { AIReasoningCard } from "../components/AIReasoningCard"
import { WebSearchCard } from "../components/WebSearchCard"
import { StreamingText, ProgressBar } from "../components/StreamingComponents"
import { useStreamingChat } from "../hooks/useStreamingChat"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
  confidence_score?: number
  detected_topic?: string
  tools_used?: string[]
  sources?: Source[]
  reasoning_steps?: ReasoningStep[]
  web_search_queries?: WebSearchQuery[]
  is_streaming?: boolean
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

interface ChatSession {
  id: string
  title: string
  created_at: string
  message_count: number
}

export default function AgriculturalAdvisor() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [currentSession, setCurrentSession] = useState<string | null>(null)
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([])
  const [userLocation, setUserLocation] = useState<{ state: string; district: string } | null>(null)
  const [isListening, setIsListening] = useState(false)
  const [isAuthenticated, setIsAuthenticated] = useState(true) // Auto-authenticate for demo
  const [showSidebar, setShowSidebar] = useState(false)
  const [expandedSources, setExpandedSources] = useState<Record<string, boolean>>({})
  const [expandedReasoning, setExpandedReasoning] = useState<Record<string, boolean>>({})
  const [expandedWebSearch, setExpandedWebSearch] = useState<Record<string, boolean>>({})
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Initialize streaming chat hook
  const { streamingState, startStreaming, stopStreaming } = useStreamingChat()

  // Update streaming message in real-time
  useEffect(() => {
    if (streamingState.streamingText && !streamingState.isStreaming) {
      // Streaming completed, update the last message
      setMessages(prev => {
        const lastMessage = prev[prev.length - 1]
        if (lastMessage && lastMessage.role === "assistant" && lastMessage.is_streaming) {
          return [
            ...prev.slice(0, -1),
            {
              ...lastMessage,
              content: streamingState.streamingText,
              is_streaming: false,
              sources: streamingState.sources,
              reasoning_steps: streamingState.reasoningSteps,
              web_search_queries: streamingState.webSearchQueries,
              confidence_score: 0.94
            }
          ]
        }
        return prev
      })
    }
  }, [streamingState.streamingText, streamingState.isStreaming, streamingState.sources, streamingState.reasoningSteps, streamingState.webSearchQueries])

  // Get user location on component mount
  useEffect(() => {
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

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: inputMessage,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    const messageToSend = inputMessage
    setInputMessage("")
    setIsLoading(true)

    try {
      // Start streaming response
      const token = localStorage.getItem("auth_token") || "demo_token"
      const sessionId = currentSession || "demo_session"
      
      await startStreaming(sessionId, messageToSend, token)

      // Create a streaming message that will be updated in real-time
      const streamingMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "",
        timestamp: new Date(),
        is_streaming: true,
        sources: streamingState.sources,
        reasoning_steps: streamingState.reasoningSteps,
        web_search_queries: streamingState.webSearchQueries
      }

      setMessages((prev) => [...prev, streamingMessage])

    } catch (error) {
      console.error("Error sending message:", error)
      // Fallback to regular response
      await new Promise((resolve) => setTimeout(resolve, 2000))

      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `Based on your query about "${messageToSend}", here's my agricultural advice for ${userLocation?.state}, ${userLocation?.district}:\n\nFor optimal crop management in your region, I recommend considering the current weather patterns and soil conditions. The monsoon season is approaching, which is ideal for rice cultivation in Punjab. Make sure to prepare your fields with proper drainage systems.\n\nKey recommendations:\n• Monitor soil moisture levels\n• Apply organic fertilizers 2 weeks before sowing\n• Consider drought-resistant varieties if rainfall is uncertain\n• Check local mandi prices for better market timing`,
        timestamp: new Date(),
        confidence_score: 0.92,
        detected_topic: "crop_management",
        tools_used: ["weather_api", "soil_database", "price_forecasting"],
        sources: [
          {
            id: 1,
            title: "Best Practices for Rice Cultivation",
            type: "Agricultural Guide",
            confidence: 0.95,
            url: "https://agriculture.punjab.gov.in/rice"
          }
        ]
      }

      setMessages((prev) => [...prev, aiResponse])
    } finally {
      setIsLoading(false)
    }
  }

  const startNewChat = () => {
    setMessages([])
    setCurrentSession(null)
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
            <Button onClick={startNewChat} className="w-full mb-4">
              <MessageCircle className="w-4 h-4 mr-2" />
              New Chat
            </Button>

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
              {chatSessions.map((session) => (
                <Button
                  key={session.id}
                  variant="ghost"
                  className="w-full justify-start text-left h-auto p-2"
                  onClick={() => setCurrentSession(session.id)}
                >
                  <div className="truncate">
                    <p className="text-sm font-medium truncate">{session.title}</p>
                    <p className="text-xs text-muted-foreground">{session.message_count} messages</p>
                  </div>
                </Button>
              ))}
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
              messages.map((message) => (
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
                        {message.role === "assistant" && message.is_streaming && streamingState.isStreaming ? (
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

                        {/* Sources Card */}
                        {(message.sources || streamingState.sources.length > 0) && (
                          <SourcesCard
                            sources={message.sources || streamingState.sources}
                            isExpanded={expandedSources[message.id] || false}
                            onToggle={() => setExpandedSources(prev => ({
                              ...prev,
                              [message.id]: !prev[message.id]
                            }))}
                          />
                        )}

                        {/* AI Reasoning Card */}
                        {(message.reasoning_steps || streamingState.reasoningSteps.length > 0) && (
                          <AIReasoningCard
                            steps={message.reasoning_steps || streamingState.reasoningSteps}
                            isExpanded={expandedReasoning[message.id] || false}
                            onToggle={() => setExpandedReasoning(prev => ({
                              ...prev,
                              [message.id]: !prev[message.id]
                            }))}
                            isProcessing={streamingState.isStreaming && streamingState.currentPhase === 'ai_reasoning'}
                          />
                        )}

                        {/* Web Search Card */}
                        {(message.web_search_queries || streamingState.webSearchQueries.length > 0) && (
                          <WebSearchCard
                            queries={message.web_search_queries || streamingState.webSearchQueries}
                            isExpanded={expandedWebSearch[message.id] || false}
                            onToggle={() => setExpandedWebSearch(prev => ({
                              ...prev,
                              [message.id]: !prev[message.id]
                            }))}
                            isSearching={streamingState.isStreaming && streamingState.currentPhase === 'web_search'}
                          />
                        )}

                        {message.role === "assistant" && !message.is_streaming && (
                          <div className="mt-2 pt-2 border-t border-border/20">
                            <div className="flex items-center gap-2 text-xs text-muted-foreground">
                              {message.confidence_score && (
                                <Badge variant="secondary" className="text-xs">
                                  {Math.round(message.confidence_score * 100)}% confident
                                </Badge>
                              )}
                              {message.detected_topic && (
                                <Badge variant="outline" className="text-xs">
                                  {message.detected_topic.replace("_", " ")}
                                </Badge>
                              )}
                              {streamingState.factCheckStatus && (
                                <Badge 
                                  variant={streamingState.factCheckStatus === 'approved' ? 'secondary' : 'destructive'} 
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
                    <p className="text-xs text-muted-foreground mt-1 px-1">{message.timestamp.toLocaleTimeString()}</p>
                  </div>
                  {message.role === "user" && (
                    <Avatar className="w-8 h-8 bg-accent">
                      <AvatarFallback>
                        <User className="w-4 h-4 text-accent-foreground" />
                      </AvatarFallback>
                    </Avatar>
                  )}
                </div>
              ))
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
                  disabled={streamingState.isStreaming}
                />
                <Button
                  size="sm"
                  variant="ghost"
                  className="absolute right-1 top-1/2 -translate-y-1/2"
                  onClick={toggleVoiceInput}
                >
                  {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                </Button>
              </div>
              <Button onClick={handleSendMessage} disabled={!inputMessage.trim() || isLoading || streamingState.isStreaming}>
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
