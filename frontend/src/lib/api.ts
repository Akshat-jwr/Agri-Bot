const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
const STREAMING_BASE_URL = process.env.NEXT_PUBLIC_STREAMING_URL || 'http://localhost:8000/api/v1/streaming'

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface User {
  id: string
  email: string
  state_name: string
  district_name: string | null
  crops_of_interest: string[]
  is_active: boolean
  is_verified: boolean
  created_at: string
}

export interface ChatSession {
  id: string
  user_id: string
  title: string
  is_active: boolean
  created_at: string
  updated_at: string
  ended_at: string | null
  primary_topic: string | null
  location_context: Record<string, any> | null
  language_preference: string
  message_count: number
  total_tokens_used: number
  satisfaction_rating: number | null
}

export interface ChatMessage {
  id: string
  session_id: string
  role: string
  content: string
  original_language: string | null
  translated_content: string | null
  created_at: string
  tokens_used: number | null
  processing_time: number | null
  confidence_score: number | null
  detected_topic: string | null
  expert_consulted: string | null
  tools_used: string[]
  fact_check_status: string | null
  accuracy_score: number | null
  user_feedback: string | null
}

export interface ApiResponse<T = any> {
  message: string
  data?: T
}

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
    this.name = 'ApiError'
  }
}

class ApiService {
  private getAuthHeaders(): HeadersInit {
    const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
    return {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    }
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}`
      try {
        const errorData = await response.json()
        errorMessage = errorData.detail || errorMessage
      } catch {
        errorMessage = response.statusText || errorMessage
      }
      throw new ApiError(response.status, errorMessage)
    }
    return response.json()
  }

  // Authentication
  async login(email: string, password: string): Promise<LoginResponse> {
    const formData = new FormData()
    formData.append('username', email)
    formData.append('password', password)

    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      body: formData
    })

    const data = await this.handleResponse<LoginResponse>(response)
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', data.access_token)
    }
    return data
  }

  async register(email: string, password: string): Promise<ApiResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    })

    return this.handleResponse<ApiResponse>(response)
  }

  // Chat Sessions
  async createChatSession(data: {
    title?: string
    language_preference?: string
    location_context?: Record<string, any>
  }): Promise<ChatSession> {
    const response = await fetch(`${API_BASE_URL}/chat/sessions`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data)
    })
    return this.handleResponse<ChatSession>(response)
  }

  async getChatSessions(page: number = 1, pageSize: number = 20): Promise<{
    sessions: ChatSession[]
    total: number
    page: number
    page_size: number
  }> {
    const response = await fetch(`${API_BASE_URL}/chat/sessions?page=${page}&page_size=${pageSize}`, {
      headers: this.getAuthHeaders()
    })
    return this.handleResponse<{
      sessions: ChatSession[]
      total: number
      page: number
      page_size: number
    }>(response)
  }

  async getChatSession(sessionId: string): Promise<ChatSession> {
    const response = await fetch(`${API_BASE_URL}/chat/sessions/${sessionId}`, {
      headers: this.getAuthHeaders()
    })
    return this.handleResponse<ChatSession>(response)
  }

  async updateChatSession(sessionId: string, data: {
    title?: string
    is_active?: boolean
    satisfaction_rating?: number
    language_preference?: string
  }): Promise<ChatSession> {
    const response = await fetch(`${API_BASE_URL}/chat/sessions/${sessionId}`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data)
    })
    return this.handleResponse<ChatSession>(response)
  }

  async deleteChatSession(sessionId: string): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${API_BASE_URL}/chat/sessions/${sessionId}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders()
    })
    return this.handleResponse<{ success: boolean; message: string }>(response)
  }

  // Chat Messages
  async sendMessage(sessionId: string, content: string, languagePreference?: string): Promise<ChatMessage[]> {
    const response = await fetch(`${API_BASE_URL}/chat/messages`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({
        session_id: sessionId,
        content,
        language_preference: languagePreference
      })
    })
    return this.handleResponse<ChatMessage[]>(response)
  }

  async getSessionMessages(sessionId: string, limit: number = 50, offset: number = 0): Promise<ChatMessage[]> {
    const response = await fetch(`${API_BASE_URL}/chat/sessions/${sessionId}/messages?limit=${limit}&offset=${offset}`, {
      headers: this.getAuthHeaders()
    })
    return this.handleResponse<ChatMessage[]>(response)
  }

  // User profile
  async getProfile(): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/users/me`, {
      headers: this.getAuthHeaders()
    })
    return this.handleResponse<User>(response)
  }

  async updateProfile(data: {
    state_name?: string
    district_name?: string
    crops_of_interest?: string[]
  }): Promise<ApiResponse> {
    const response = await fetch(`${API_BASE_URL}/users/me`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data)
    })
    return this.handleResponse<ApiResponse>(response)
  }

  // EventSource for streaming
  createStreamingEventSource(sessionId: string, content: string, token?: string): EventSource {
    const authToken = token || (typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null)
    if (!authToken) {
      throw new Error('No authentication token found')
    }

    const url = `${STREAMING_BASE_URL}/chat?session_id=${encodeURIComponent(sessionId)}&content=${encodeURIComponent(content)}&token=${encodeURIComponent(authToken)}`
    
    console.log('🔗 Creating EventSource:', url.replace(/token=[^&]+/, 'token=***'))
    
    const eventSource = new EventSource(url)
    
    eventSource.onopen = () => {
      console.log('✅ EventSource Connected!')
    }
    
    eventSource.onerror = (error) => {
      console.error('❌ EventSource Error:', error)
    }
    
    return eventSource
  }

  // Logout
  logout(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token')
    }
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return typeof window !== 'undefined' ? !!localStorage.getItem('auth_token') : false
  }
}

export const apiService = new ApiService()
export { ApiError }
