"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { MessageCircle, MapPin, Settings, LogOut, Sprout } from "lucide-react"

interface ChatSession {
  id: string
  title: string
  created_at: string
  message_count: number
}

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
  userLocation: { state: string; district: string } | null
  chatSessions: ChatSession[]
  onNewChat: () => void
  onSelectSession: (sessionId: string) => void
  onLogout: () => void
}

export function Sidebar({
  isOpen,
  onClose,
  userLocation,
  chatSessions,
  onNewChat,
  onSelectSession,
  onLogout,
}: SidebarProps) {
  return (
    <>
      <div
        className={`${
          isOpen ? "translate-x-0" : "-translate-x-full"
        } fixed inset-y-0 left-0 z-50 w-64 bg-sidebar border-r border-sidebar-border transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0`}
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
            <Button onClick={onNewChat} className="w-full mb-4">
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
                  onClick={() => onSelectSession(session.id)}
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
              <Button variant="ghost" className="w-full justify-start" onClick={onLogout}>
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </div>

      {isOpen && <div className="fixed inset-0 bg-black/50 z-40 lg:hidden" onClick={onClose} />}
    </>
  )
}
