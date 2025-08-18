"use client"

import { useState, useEffect } from "react"

interface Location {
  state: string
  district: string
}

export function useLocation() {
  const [location, setLocation] = useState<Location | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          // In a real app, you'd reverse geocode to get state/district
          // For demo, we'll use placeholder data based on coordinates
          setLocation({ state: "Punjab", district: "Ludhiana" })
          setIsLoading(false)
        },
        (error) => {
          console.log("Location access denied, using fallback")
          setLocation({ state: "India", district: "All Districts" })
          setIsLoading(false)
        },
      )
    } else {
      setLocation({ state: "India", district: "All Districts" })
      setIsLoading(false)
    }
  }, [])

  return { location, isLoading }
}
