"use client"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Send, Bot, User, Mic, MicOff } from "lucide-react"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
  confidence_score?: number
  detected_topic?: string
  tools_used?: string[]
}

interface ChatInterfaceProps {
  messages: Message[]
  onSendMessage: (message: string) => void
  isLoading: boolean
}

export function ChatInterface({ messages, onSendMessage, isLoading }: ChatInterfaceProps) {
  const [inputMessage, setInputMessage] = useState("")
  const [isListening, setIsListening] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const handleSendMessage = () => {
    if (!inputMessage.trim() || isLoading) return
    onSendMessage(inputMessage)
    setInputMessage("")
  }

  const toggleVoiceInput = () => {
    setIsListening(!isListening)
    // Web Speech API implementation would go here
  }

  return (
    <div className="flex flex-col h-full">
      <ScrollArea className="flex-1 p-4">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.length === 0 ? (
            <WelcomeScreen onQuickAction={setInputMessage} />
          ) : (
            messages.map((message) => <MessageBubble key={message.id} message={message} />)
          )}
          {isLoading && <LoadingMessage />}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      <div className="border-t border-border p-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <Input
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Ask about crops, weather, market prices, or farming techniques..."
                onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
                className="pr-12"
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
            <Button onClick={handleSendMessage} disabled={!inputMessage.trim() || isLoading}>
              <Send className="w-4 h-4" />
            </Button>
          </div>
          <p className="text-xs text-muted-foreground mt-2 text-center">
            KrishiMitra can make mistakes. Please verify important agricultural decisions.
          </p>
        </div>
      </div>
    </div>
  )
}

function MessageBubble({ message }: { message: Message }) {
  return (
    <div className={`flex gap-3 ${message.role === "user" ? "justify-end" : "justify-start"}`}>
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
            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
            {message.role === "assistant" && (
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
  )
}

function WelcomeScreen({ onQuickAction }: { onQuickAction: (message: string) => void }) {
  const quickActions = [
    {
      title: "Crop Recommendations",
      description: "Get personalized crop suggestions",
      action: "What crops should I plant this season?",
    },
    {
      title: "Market Prices",
      description: "Check latest mandi rates",
      action: "What are the current market prices?",
    },
    {
      title: "Weather Forecast",
      description: "Get farming-focused weather updates",
      action: "How's the weather looking for farming?",
    },
    {
      title: "Pest Management",
      description: "Learn about pest prevention",
      action: "Help me with pest control",
    },
  ]

  return (
    <div className="text-center py-12">
      <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
        <Bot className="w-8 h-8 text-primary" />
      </div>
      <h2 className="text-xl font-semibold mb-2">Welcome to KrishiMitra!</h2>
      <p className="text-muted-foreground mb-6">
        Your AI-powered agricultural advisor. Ask me about crops, weather, market prices, or farming techniques.
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
        {quickActions.map((item, index) => (
          <Card
            key={index}
            className="cursor-pointer hover:bg-accent/5 transition-colors"
            onClick={() => onQuickAction(item.action)}
          >
            <CardContent className="p-4">
              <h3 className="font-medium mb-1">{item.title}</h3>
              <p className="text-sm text-muted-foreground">{item.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

function LoadingMessage() {
  return (
    <div className="flex gap-3 justify-start">
      <Avatar className="w-8 h-8 bg-primary">
        <AvatarFallback>
          <Bot className="w-4 h-4 text-primary-foreground" />
        </AvatarFallback>
      </Avatar>
      <Card className="bg-card">
        <CardContent className="p-3">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-primary rounded-full animate-bounce"></div>
            <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "0.1s" }}></div>
            <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
            <span className="text-sm text-muted-foreground ml-2">Analyzing your query...</span>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
