import React from 'react'
import { Card, CardContent } from "./ui/card"
import { Badge } from "./ui/badge"
import { Button } from "./ui/button"
import { ChevronDown, ChevronUp, ExternalLink, FileText, Globe, TrendingUp } from "lucide-react"

interface Source {
  id: number
  title: string
  type: string
  confidence: number
  url: string
  excerpt?: string
}

interface SourcesCardProps {
  sources: Source[]
  isExpanded: boolean
  onToggle: () => void
}

export function SourcesCard({ sources, isExpanded, onToggle }: SourcesCardProps) {
  if (!sources || sources.length === 0) return null

  const getSourceIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'research paper':
        return <FileText className="w-4 h-4" />
      case 'agricultural guide':
        return <FileText className="w-4 h-4" />
      case 'market data':
        return <TrendingUp className="w-4 h-4" />
      default:
        return <Globe className="w-4 h-4" />
    }
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return "bg-green-500"
    if (confidence >= 0.8) return "bg-yellow-500"
    return "bg-orange-500"
  }

  return (
    <Card className="mt-3 border-l-4 border-l-blue-500 bg-gradient-to-r from-blue-50/50 to-transparent">
      <CardContent className="p-3">
        <Button
          variant="ghost"
          onClick={onToggle}
          className="w-full justify-between p-0 h-auto hover:bg-transparent"
        >
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-blue-600" />
            <span className="font-medium text-sm">Sources ({sources.length})</span>
            <Badge variant="secondary" className="text-xs">
              Verified
            </Badge>
          </div>
          {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </Button>

        {isExpanded && (
          <div className="mt-3 space-y-2">
            {sources.map((source) => (
              <div
                key={source.id}
                className="flex items-start gap-3 p-2 rounded-lg bg-white/60 hover:bg-white/80 transition-colors border border-gray-100"
              >
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  <div className="text-gray-600">
                    {getSourceIcon(source.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {source.title}
                    </p>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant="outline" className="text-xs">
                        {source.type}
                      </Badge>
                      <div className="flex items-center gap-1">
                        <div
                          className={`w-2 h-2 rounded-full ${getConfidenceColor(source.confidence)}`}
                        />
                        <span className="text-xs text-gray-500">
                          {Math.round(source.confidence * 100)}% match
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                <Button
                  size="sm"
                  variant="ghost"
                  className="p-1 h-6 w-6"
                  onClick={() => window.open(source.url, '_blank')}
                >
                  <ExternalLink className="w-3 h-3" />
                </Button>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
