"use client"

import React, { createContext, useContext, useEffect, useState } from 'react'
import { apiService, User, ApiError } from '../lib/api'

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string) => Promise<string>
  logout: () => void
  updateLocation: (state: string, district: string) => Promise<void>
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const isAuthenticated = !!user && apiService.isAuthenticated()

  const fetchUser = async () => {
    try {
      if (apiService.isAuthenticated()) {
        const userData = await apiService.getProfile()
        setUser(userData)
      }
    } catch (error) {
      console.error('Failed to fetch user:', error)
      // If token is invalid, logout
      apiService.logout()
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchUser()
  }, [])

  const login = async (email: string, password: string) => {
    setLoading(true)
    try {
      await apiService.login(email, password)
      await fetchUser()
    } catch (error) {
      setLoading(false)
      throw error
    }
  }

  const register = async (email: string, password: string): Promise<string> => {
    const response = await apiService.register(email, password)
    return response.message
  }

  const logout = () => {
    apiService.logout()
    setUser(null)
  }

  const updateLocation = async (state: string, district: string) => {
    if (!user) throw new Error('User not authenticated')
    
    await apiService.updateProfile({
      state_name: state,
      district_name: district
    })
    
    // Refresh user data
    await fetchUser()
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        logout,
        updateLocation,
        isAuthenticated
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
