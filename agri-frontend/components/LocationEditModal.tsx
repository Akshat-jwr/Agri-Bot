"use client"

import { useState, useEffect } from "react"
import { Button } from "./ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card"
import { Input } from "./ui/input"
import { MapPin, Save, X } from "lucide-react"
import { useAuth } from "../context/AuthContext"

interface LocationEditModalProps {
  isOpen: boolean
  onClose: () => void
  currentState: string
  currentDistrict: string | null
}

export default function LocationEditModal({ 
  isOpen, 
  onClose, 
  currentState, 
  currentDistrict 
}: LocationEditModalProps) {
  const [state, setState] = useState(currentState)
  const [district, setDistrict] = useState(currentDistrict || "")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const { updateLocation } = useAuth()

  useEffect(() => {
    setState(currentState)
    setDistrict(currentDistrict || "")
  }, [currentState, currentDistrict])

  const handleSave = async () => {
    if (!state.trim() || !district.trim()) {
      setError("Both state and district are required")
      return
    }

    setLoading(true)
    setError("")

    try {
      await updateLocation(state.trim(), district.trim())
      onClose()
    } catch (error: any) {
      setError(error?.message || "Failed to update location")
    } finally {
      setLoading(false)
    }
  }

  const handleGetCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          // In a real app, you'd reverse geocode these coordinates
          // For now, we'll just set some sample data
          setState("Punjab")
          setDistrict("Ludhiana")
        },
        (error) => {
          setError("Unable to get current location. Please enter manually.")
        }
      )
    } else {
      setError("Geolocation is not supported by this browser")
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <MapPin className="w-5 h-5 text-primary" />
              Update Location
            </CardTitle>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="w-4 h-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Current Location Button */}
          <Button
            variant="outline"
            className="w-full"
            onClick={handleGetCurrentLocation}
          >
            <MapPin className="w-4 h-4 mr-2" />
            Use Current Location
          </Button>

          {/* State Input */}
          <div className="space-y-2">
            <label className="text-sm font-medium">State</label>
            <Input
              placeholder="Enter your state"
              value={state}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setState(e.target.value)}
            />
          </div>

          {/* District Input */}
          <div className="space-y-2">
            <label className="text-sm font-medium">District</label>
            <Input
              placeholder="Enter your district"
              value={district}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setDistrict(e.target.value)}
            />
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
              <p className="text-sm text-destructive">{error}</p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-2">
            <Button variant="outline" onClick={onClose} className="flex-1">
              Cancel
            </Button>
            <Button onClick={handleSave} disabled={loading} className="flex-1">
              {loading ? (
                <>
                  <Save className="w-4 h-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4 mr-2" />
                  Save
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
