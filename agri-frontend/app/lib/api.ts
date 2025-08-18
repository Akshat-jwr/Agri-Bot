"use client"

// API configuration and helper functions
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
  confidence_score?: number
  detected_topic?: string
  tools_used?: string[]
}

export interface ChatSession {
  id: string
  title: string
  created_at: string
  message_count: number
}

export class ApiClient {
  private baseUrl: string
  private token: string | null

  constructor() {
    this.baseUrl = API_BASE_URL
    this.token = typeof window !== "undefined" ? localStorage.getItem("auth_token") : null
  }

  private async request(endpoint: string, options: RequestInit = {}) {
    const url = `${this.baseUrl}${endpoint}`
    const headers = {
      "Content-Type": "application/json",
      ...(this.token && { Authorization: `Bearer ${this.token}` }),
      ...options.headers,
    }

    const response = await fetch(url, {
      ...options,
      headers,
    })

    if (!response.ok) {
      throw new Error(`API request failed: ${response.statusText}`)
    }

    return response.json()
  }

  async sendMessage(message: string, sessionId?: string): Promise<Message> {
    const response = await this.request("/chat/send", {
      method: "POST",
      body: JSON.stringify({
        message,
        session_id: sessionId,
      }),
    })

    return {
      id: response.id,
      role: "assistant",
      content: response.content,
      timestamp: new Date(response.timestamp),
      confidence_score: response.confidence_score,
      detected_topic: response.detected_topic,
      tools_used: response.tools_used,
    }
  }

  async getChatSessions(): Promise<ChatSession[]> {
    return this.request("/chat/sessions")
  }

  async getSessionMessages(sessionId: string): Promise<Message[]> {
    const response = await this.request(`/chat/sessions/${sessionId}/messages`)
    return response.map((msg: any) => ({
      ...msg,
      timestamp: new Date(msg.timestamp),
    }))
  }

  async createNewSession(): Promise<string> {
    const response = await this.request("/chat/sessions", {
      method: "POST",
    })
    return response.session_id
  }
}

export const apiClient = new ApiClient()
