export interface AgricultureQuestion {
  id: string;
  question: string;
  timestamp: Date;
  language: 'en' | 'hi' | 'auto';
}

export interface AgricultureResponse {
  id: string;
  response: string;
  sources: Source[];
  aiReasoning: AIReasoningStep[];
  confidence: number;
  timestamp: Date;
  language: 'en' | 'hi';
}

export interface Source {
  id: string;
  title: string;
  url?: string;
  content: string;
  confidence: number;
  relevanceScore: number;
  type: 'document' | 'web' | 'database' | 'expert';
}

export interface AIReasoningStep {
  id: string;
  step: number;
  title: string;
  description: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  timestamp: Date;
  confidence?: number;
}

export interface StreamingProgress {
  currentStep: number;
  totalSteps: number;
  stepName: string;
  percentage: number;
  status: 'idle' | 'processing' | 'completed' | 'error';
}

export interface WebSearchQuery {
  query: string;
  language: string;
  timestamp: Date;
  results?: number;
}

export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: Source[];
  aiReasoning?: AIReasoningStep[];
  confidence?: number;
  language?: 'en' | 'hi';
}

export interface StreamingState {
  isStreaming: boolean;
  progress: StreamingProgress;
  currentMessage: Partial<AgricultureResponse>;
  error?: string;
}
