import React from 'react'
import { Card, CardContent } from "./ui/card"
import { Badge } from "./ui/badge"
import { Button } from "./ui/button"
import { ChevronDown, ChevronUp, CheckCircle, AlertTriangle, Info, Clock } from "lucide-react"

interface FactCheckStep {
  step: string
  index: number
}

interface FactCheckCardProps {
  steps: FactCheckStep[]
  corrections: string
  status: string
  confidence?: number
  isExpanded: boolean
  onToggle: () => void
  isProcessing?: boolean
}

export function FactCheckCard({ 
  steps, 
  corrections, 
  status, 
  confidence, 
  isExpanded, 
  onToggle, 
  isProcessing = false 
}: FactCheckCardProps) {
  if (!steps || (steps.length === 0 && !corrections && !status)) return null

  const getStatusIcon = () => {
    if (isProcessing) return <Clock className="w-4 h-4 text-blue-600 animate-spin" />
    
    switch (status) {
      case 'approved':
        return <CheckCircle className="w-4 h-4 text-green-600" />
      case 'corrected':
        return <AlertTriangle className="w-4 h-4 text-yellow-600" />
      case 'flagged':
        return <AlertTriangle className="w-4 h-4 text-red-600" />
      default:
        return <Info className="w-4 h-4 text-blue-600" />
    }
  }

  const getStatusColor = () => {
    switch (status) {
      case 'approved':
        return 'border-l-green-500 bg-gradient-to-r from-green-50/50 to-transparent'
      case 'corrected':
        return 'border-l-yellow-500 bg-gradient-to-r from-yellow-50/50 to-transparent'
      case 'flagged':
        return 'border-l-red-500 bg-gradient-to-r from-red-50/50 to-transparent'
      default:
        return 'border-l-blue-500 bg-gradient-to-r from-blue-50/50 to-transparent'
    }
  }

  const getStatusText = () => {
    switch (status) {
      case 'approved':
        return 'Fact-Checked & Verified'
      case 'corrected':
        return 'Enhanced with Corrections'
      case 'flagged':
        return 'Requires Attention'
      default:
        return 'Fact Checking'
    }
  }

  return (
    <Card className={`mt-3 border-l-4 ${getStatusColor()}`}>
      <CardContent className="p-3">
        <Button
          variant="ghost"
          onClick={onToggle}
          className="w-full justify-between p-0 h-auto hover:bg-transparent"
        >
          <div className="flex items-center gap-2">
            {getStatusIcon()}
            <span className="font-medium text-sm">{getStatusText()}</span>
            {confidence && !isProcessing && (
              <Badge variant="secondary" className="text-xs">
                {Math.round(confidence * 100)}% confidence
              </Badge>
            )}
            {isProcessing && (
              <Badge variant="secondary" className="text-xs animate-pulse">
                Processing...
              </Badge>
            )}
          </div>
          {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </Button>

        {isExpanded && (
          <div className="mt-3 space-y-3">
            {/* Fact Check Steps */}
            {steps && steps.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                  <CheckCircle className="w-3 h-3 text-blue-600" />
                  Verification Process
                </h4>
                <div className="space-y-2">
                  {steps.map((step, index) => (
                    <div
                      key={index}
                      className={`p-2 rounded-lg border transition-all duration-300 ${
                        isProcessing && index === steps.length - 1
                          ? 'bg-blue-50 border-blue-200 animate-pulse'
                          : 'bg-white/60 border-gray-200'
                      }`}
                    >
                      <div className="flex items-start gap-2">
                        <div className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-medium mt-0.5 flex-shrink-0 ${
                          isProcessing && index === steps.length - 1
                            ? 'bg-blue-100 text-blue-700'
                            : 'bg-green-100 text-green-700'
                        }`}>
                          {index + 1}
                        </div>
                        <p className="text-sm text-gray-700 flex-1">
                          {step.step}
                        </p>
                        {!isProcessing && (
                          <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Fact Check Corrections */}
            {corrections && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                  <AlertTriangle className="w-3 h-3 text-yellow-600" />
                  Enhanced Information
                </h4>
                <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <div className="prose prose-sm max-w-none">
                    {corrections.split('\n').map((line, index) => (
                      <p key={index} className="text-sm text-gray-700 mb-1 last:mb-0">
                        {line}
                      </p>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Status Summary */}
            {status && !isProcessing && (
              <div className="pt-2 border-t border-gray-100">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {getStatusIcon()}
                    <span className="text-xs font-medium text-gray-600">
                      Verification Status: {getStatusText()}
                    </span>
                  </div>
                  {confidence && (
                    <Badge 
                      variant={status === 'approved' ? 'secondary' : 'outline'} 
                      className="text-xs"
                    >
                      {Math.round(confidence * 100)}% confident
                    </Badge>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
