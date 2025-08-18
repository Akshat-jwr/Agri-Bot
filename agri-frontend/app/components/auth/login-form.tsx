"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Sprout } from "lucide-react"

interface LoginFormProps {
  onLogin: () => void
}

export function LoginForm({ onLogin }: LoginFormProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 to-accent/5 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto w-16 h-16 bg-primary rounded-full flex items-center justify-center mb-4">
            <Sprout className="w-8 h-8 text-primary-foreground" />
          </div>
          <CardTitle className="text-2xl font-bold text-primary">KrishiMitra</CardTitle>
          <p className="text-muted-foreground">Your AI Agricultural Advisor</p>
        </CardHeader>
        <CardContent className="space-y-4">
          <Button className="w-full" onClick={onLogin}>
            Login with Demo Account
          </Button>
          <p className="text-xs text-center text-muted-foreground">Demo: demo@farmer.com / demo123</p>
        </CardContent>
      </Card>
    </div>
  )
}
