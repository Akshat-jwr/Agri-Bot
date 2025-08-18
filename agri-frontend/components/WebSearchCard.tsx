import React from 'react'
import { Card, CardContent } from "./ui/card"
import { Badge } from "./ui/badge"
import { Button } from "./ui/button"
import { ChevronDown, ChevronUp, Search, Globe, Clock } from "lucide-react"

interface WebSearchQuery {
  query: string
  timestamp?: Date
  results?: number
}

interface WebSearchCardProps {
  queries: WebSearchQuery[]
  isExpanded: boolean
  onToggle: () => void
  isSearching?: boolean
}

export function WebSearchCard({ queries, isExpanded, onToggle, isSearching = false }: WebSearchCardProps) {
  if (!queries || queries.length === 0) return null

  return (
    <Card className="mt-3 border-l-4 border-l-orange-500 bg-gradient-to-r from-orange-50/50 to-transparent">
      <CardContent className="p-3">
        <Button
          variant="ghost"
          onClick={onToggle}
          className="w-full justify-between p-0 h-auto hover:bg-transparent"
        >
          <div className="flex items-center gap-2">
            <Search className="w-4 h-4 text-orange-600" />
            <span className="font-medium text-sm">Web Search Queries ({queries.length})</span>
            {isSearching && (
              <Badge variant="secondary" className="text-xs animate-pulse">
                Searching...
              </Badge>
            )}
          </div>
          {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </Button>

        {isExpanded && (
          <div className="mt-3 space-y-2">
            {queries.map((query, index) => (
              <div
                key={index}
                className={`p-3 rounded-lg border transition-all duration-300 ${
                  isSearching && index === queries.length - 1
                    ? 'bg-orange-50 border-orange-200 animate-pulse'
                    : 'bg-white/60 border-gray-200 hover:bg-white/80'
                }`}
              >
                <div className="flex items-start gap-2">
                  <Globe className="w-4 h-4 text-orange-600 mt-0.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-900 break-words">
                      "{query.query}"
                    </p>
                    <div className="flex items-center gap-2 mt-1">
                      {query.timestamp && (
                        <div className="flex items-center gap-1">
                          <Clock className="w-3 h-3 text-gray-400" />
                          <span className="text-xs text-gray-500">
                            {query.timestamp.toLocaleTimeString()}
                          </span>
                        </div>
                      )}
                      {query.results && (
                        <Badge variant="outline" className="text-xs">
                          {query.results} results
                        </Badge>
                      )}
                      {isSearching && index === queries.length - 1 && (
                        <Badge variant="secondary" className="text-xs">
                          Searching...
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
