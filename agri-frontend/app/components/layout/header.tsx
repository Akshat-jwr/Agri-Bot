"use client"

import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { History, CloudRain, TrendingUp } from "lucide-react"

interface HeaderProps {
  onToggleSidebar: () => void
}

export function Header({ onToggleSidebar }: HeaderProps) {
  return (
    <div className="bg-card border-b border-border p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" className="lg:hidden" onClick={onToggleSidebar}>
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
  )
}
