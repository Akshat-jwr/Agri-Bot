import React, { useState } from 'react'
import { Card, CardContent } from "./ui/card"
import { Badge } from "./ui/badge"
import { Button } from "./ui/button"
import { ChevronDown, ChevronUp, Brain, Lightbulb, CheckCircle } from "lucide-react"

interface ReasoningStep {
  step: string
  index: number
  completed?: boolean
}

interface AIReasoningCardProps {
  steps: ReasoningStep[]
  isExpanded: boolean
  onToggle: () => void
  isProcessing?: boolean
}

export function AIReasoningCard({ steps, isExpanded, onToggle, isProcessing = false }: AIReasoningCardProps) {
  if (!steps || steps.length === 0) return null

  return (
    <Card className="mt-3 border-l-4 border-l-purple-500 bg-gradient-to-r from-purple-50/50 to-transparent">
      <CardContent className="p-3">
        <Button
          variant="ghost"
          onClick={onToggle}
          className="w-full justify-between p-0 h-auto hover:bg-transparent"
        >
          <div className="flex items-center gap-2">
            <Brain className="w-4 h-4 text-purple-600" />
            <span className="font-medium text-sm">AI Reasoning Process</span>
            {isProcessing && (
              <div className="flex gap-1">
                <div className="w-1 h-1 bg-purple-500 rounded-full animate-bounce" />
                <div className="w-1 h-1 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                <div className="w-1 h-1 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
              </div>
            )}
          </div>
          {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </Button>

        {isExpanded && (
          <div className="mt-3 space-y-2">
            {steps.map((reasoning, index) => (
              <div
                key={index}
                className={`flex items-start gap-3 p-2 rounded-lg transition-all duration-300 ${
                  reasoning.completed 
                    ? 'bg-green-50 border border-green-200' 
                    : isProcessing && index === steps.length - 1
                    ? 'bg-purple-50 border border-purple-200 animate-pulse'
                    : 'bg-gray-50 border border-gray-200'
                }`}
              >
                <div className="flex-shrink-0 mt-0.5">
                  {reasoning.completed ? (
                    <CheckCircle className="w-4 h-4 text-green-600" />
                  ) : isProcessing && index === steps.length - 1 ? (
                    <div className="w-4 h-4 border-2 border-purple-600 border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <Lightbulb className="w-4 h-4 text-gray-400" />
                  )}
                </div>
                <div className="flex-1">
                  <p className={`text-sm ${
                    reasoning.completed 
                      ? 'text-green-800' 
                      : isProcessing && index === steps.length - 1
                      ? 'text-purple-800 font-medium'
                      : 'text-gray-600'
                  }`}>
                    {reasoning.step}
                  </p>
                </div>
              </div>
            ))}
            
            {isProcessing && (
              <div className="text-xs text-purple-600 font-medium text-center py-2">
                🧠 AI is analyzing your agricultural query...
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
