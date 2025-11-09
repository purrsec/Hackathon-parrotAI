'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { 
  Send, 
  Loader2, 
  AlertCircle, 
  CheckCircle2, 
  XCircle, 
  Plane, 
  Bot, 
  User, 
  Rocket, 
  BarChart3, 
  ClipboardList, 
  Clock, 
  Lightbulb 
} from 'lucide-react'
import { ChatMessage, ServerMessage, UserMessage } from '@/types/chat'

// Simple ID generator
const generateId = () => {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
}

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws'

export default function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [isConnected, setIsConnected] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)
  const [pendingMissionId, setPendingMissionId] = useState<string | null>(null)
  const [userId] = useState(() => `user-${generateId().slice(0, 8)}`)
  const wsRef = useRef<WebSocket | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleServerMessage = useCallback((data: ServerMessage) => {
    switch (data.type) {
      case 'welcome':
        setMessages((prev) => [
          ...prev,
          {
            id: `msg-${Date.now()}`,
            role: 'system',
            content: data.message,
            timestamp: new Date(),
            type: 'welcome',
          },
        ])
        break

      case 'message_processed':
        const understanding = data.mission_dsl?.understanding
        const content = understanding
          ? `${data.message}\n\nUnderstanding: ${understanding}`
          : data.message

        setMessages((prev) => [
          ...prev,
          {
            id: data.id || `msg-${Date.now()}`,
            role: 'assistant',
            content,
            timestamp: new Date(data.timestamp || new Date().toISOString()),
            missionDSL: data.mission_dsl,
            type: 'message_processed',
          },
        ])

        // If mission DSL was generated, store the mission ID for confirmation
        if (data.mission_dsl && data.status === 'processed') {
          setPendingMissionId(data.id || null)
        }
        break

      case 'mission_confirmation':
        setPendingMissionId(data.id || null)
        setMessages((prev) => [
          ...prev,
          {
            id: `mission-confirm-${Date.now()}`,
            role: 'assistant',
            content: `Mission loaded on drone\n\nDrone ID: ${data.drone_id || 'N/A'}\nIP Address: ${data.drone_ip || 'N/A'}\n\n${data.message}`,
            timestamp: new Date(data.timestamp || new Date().toISOString()),
            type: 'mission_confirmation',
          },
        ])
        break

      case 'mission_confirmed':
        setPendingMissionId(null)
        setMessages((prev) => [
          ...prev,
          {
            id: `mission-confirmed-${Date.now()}`,
            role: 'assistant',
            content: `Mission confirmed\n\n${data.message}\nStatus: ${data.status}`,
            timestamp: new Date(data.timestamp || new Date().toISOString()),
            type: 'mission_confirmed',
          },
        ])
        break

      case 'mission_cancelled':
        setPendingMissionId(null)
        setMessages((prev) => [
          ...prev,
          {
            id: `mission-cancelled-${Date.now()}`,
            role: 'assistant',
            content: `Mission cancelled\n\n${data.message}`,
            timestamp: new Date(data.timestamp || new Date().toISOString()),
            type: 'mission_cancelled',
          },
        ])
        break

      case 'mission_execution_starting':
        setMessages((prev) => [
          ...prev,
          {
            id: `mission-starting-${Date.now()}`,
            role: 'assistant',
            content: `Mission execution started\n\n${data.message}`,
            timestamp: new Date(data.timestamp || new Date().toISOString()),
            type: 'mission_execution_starting',
          },
        ])
        break

      case 'mission_execution_result':
        setMessages((prev) => [
          ...prev,
          {
            id: `mission-result-${Date.now()}`,
            role: 'assistant',
            content: `Mission result\n\nStatus: ${data.status}\n\n${JSON.stringify(data.report, null, 2)}`,
            timestamp: new Date(data.timestamp || new Date().toISOString()),
            type: 'mission_execution_result',
          },
        ])
        break

      case 'mission_execution_blocked':
        setMessages((prev) => [
          ...prev,
          {
            id: `mission-blocked-${Date.now()}`,
            role: 'assistant',
            content: `Execution blocked\n\n${data.message}\nReason: ${data.reason}`,
            timestamp: new Date(data.timestamp || new Date().toISOString()),
            type: 'mission_execution_blocked',
          },
        ])
        break

      case 'error':
        setMessages((prev) => [
          ...prev,
          {
            id: `error-${Date.now()}`,
            role: 'assistant',
            content: `Error: ${data.message}`,
            timestamp: new Date(data.timestamp || new Date().toISOString()),
            type: 'error',
          },
        ])
        break

      default:
        console.log('Unknown message type:', data.type)
    }
  }, [])

  const connectWebSocket = useCallback(() => {
    setIsConnecting(true)
    try {
      const ws = new WebSocket(WS_URL)
      wsRef.current = ws

      ws.onopen = () => {
        setIsConnected(true)
        setIsConnecting(false)
        console.log('Connected to WebSocket')
      }

      ws.onmessage = (event) => {
        try {
          const data: ServerMessage = JSON.parse(event.data)
          handleServerMessage(data)
        } catch (error) {
          console.error('Error parsing message:', error)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        setIsConnecting(false)
        setIsConnected(false)
      }

      ws.onclose = () => {
        setIsConnected(false)
        setIsConnecting(false)
        console.log('WebSocket disconnected')
        // Attempting to reconnect after 3 seconds
        setTimeout(() => {
          if (!wsRef.current || wsRef.current.readyState === WebSocket.CLOSED) {
            connectWebSocket()
          }
        }, 3000)
      }
    } catch (error) {
      console.error('Failed to connect:', error)
      setIsConnecting(false)
      setIsConnected(false)
    }
  }, [handleServerMessage])

  // Connect to WebSocket
  useEffect(() => {
    connectWebSocket()
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [connectWebSocket])

  const sendMessage = () => {
    if (!input.trim() || !isConnected || !wsRef.current) return

    const messageId = `msg-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
    const userMessage: UserMessage = {
      id: messageId,
      message: input.trim(),
      source: 'nextjs',
      user_id: userId,
    }

    // Check if this is a confirmation response (including "dry" for simulation)
    const inputLower = input.trim().toLowerCase()
    const isConfirmation = inputLower === 'yes' || inputLower === 'y' || inputLower === 'oui' || 
                          inputLower === 'no' || inputLower === 'n' || inputLower === 'non' ||
                          inputLower === 'dry'
    const isDryRun = inputLower === 'dry'

    if (isConfirmation && pendingMissionId) {
      userMessage.is_confirmation = true
      userMessage.confirmation_for = pendingMissionId
      // "dry" is treated as "yes" but with dry_run flag
      userMessage.confirmation_value = inputLower === 'yes' || inputLower === 'y' || inputLower === 'oui' || isDryRun
      if (isDryRun) {
        userMessage.metadata = { ...userMessage.metadata, dry_run: true }
      }
    }

    // Add user message to UI (hide "dry" and show "yes" instead)
    const displayContent = isDryRun ? 'yes' : input.trim()
    setMessages((prev) => [
      ...prev,
      {
        id: messageId,
        role: 'user',
        content: displayContent,
        timestamp: new Date(),
      },
    ])

    // Send to server
    wsRef.current.send(JSON.stringify(userMessage))
    setInput('')
    setPendingMissionId(null) // Clear pending mission after sending confirmation
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const getMessageIcon = (type?: string) => {
    switch (type) {
      case 'welcome':
        return <CheckCircle2 className="w-5 h-5 text-green-500" />
      case 'mission_confirmation':
        return <Plane className="w-5 h-5 text-blue-500" />
      case 'mission_confirmed':
        return <CheckCircle2 className="w-5 h-5 text-green-500" />
      case 'mission_cancelled':
        return <XCircle className="w-5 h-5 text-red-500" />
      case 'mission_execution_starting':
        return <Rocket className="w-5 h-5 text-blue-500" />
      case 'mission_execution_result':
        return <BarChart3 className="w-5 h-5 text-green-500" />
      case 'mission_execution_blocked':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-500" />
      default:
        return <Bot className="w-5 h-5 text-blue-500" />
    }
  }

  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-900">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center text-gray-500 dark:text-gray-400">
            <Plane className="w-16 h-16 mb-4 text-gray-400" />
            <h2 className="text-xl font-semibold mb-2">Welcome to Parrot AI</h2>
            <p className="text-sm max-w-md">
              Send natural language commands to control your drone.
              <br />
              Example: &quot;go inspect the tower at 30 meters&quot;
            </p>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            {message.role !== 'user' && (
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-500 dark:bg-blue-600 flex items-center justify-center text-white">
                {getMessageIcon(message.type)}
              </div>
            )}

            <div
              className={`max-w-[80%] rounded-lg px-4 py-2 ${
                message.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : message.role === 'system'
                  ? 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100'
              }`}
            >
              <div className="whitespace-pre-wrap break-words">{message.content}</div>
              {message.missionDSL && (
                <div className="mt-2 pt-2 border-t border-gray-300 dark:border-gray-600">
                  <details className="text-xs">
                    <summary className="cursor-pointer font-semibold flex items-center gap-1">
                      <ClipboardList className="w-3 h-3 inline" />
                      Mission DSL ({message.missionDSL.segments?.length || 0} segments)
                    </summary>
                    <pre className="mt-2 p-2 bg-gray-200 dark:bg-gray-700 rounded text-xs overflow-x-auto">
                      {JSON.stringify(message.missionDSL, null, 2)}
                    </pre>
                  </details>
                </div>
              )}
              <div className="text-xs opacity-70 mt-1">
                {message.timestamp.toLocaleTimeString('en-US', {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </div>
            </div>

            {message.role === 'user' && (
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-300 dark:bg-gray-700 flex items-center justify-center text-gray-700 dark:text-gray-300">
                <User className="w-5 h-5" />
              </div>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Connection status */}
      <div className="px-4 py-2 border-t border-gray-200 dark:border-gray-800">
        <div className="flex items-center gap-2 text-xs">
          <div
            className={`w-2 h-2 rounded-full ${
              isConnected ? 'bg-green-500' : isConnecting ? 'bg-yellow-500 animate-pulse' : 'bg-red-500'
            }`}
          />
          <span className="text-gray-600 dark:text-gray-400">
            {isConnected
              ? 'Connected'
              : isConnecting
              ? 'Connecting...'
              : 'Disconnected'}
          </span>
          {pendingMissionId && (
            <span className="ml-auto text-blue-600 dark:text-blue-400 flex items-center gap-1">
              <Clock className="w-3 h-3" />
              Mission pending confirmation
            </span>
          )}
        </div>
      </div>

      {/* Input area */}
      <div className="border-t border-gray-200 dark:border-gray-800 p-4">
        <div className="flex gap-2 items-end">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={
              pendingMissionId
                ? 'Type "yes" or "no" to confirm/cancel the mission...'
                : 'Type your message... (Enter to send)'
            }
            className="flex-1 min-h-[44px] max-h-32 px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            rows={1}
            disabled={!isConnected}
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || !isConnected}
            className="px-4 py-2 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center gap-2 min-h-[44px]"
          >
            {isConnecting ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
        {pendingMissionId && (
          <div className="mt-2 text-xs text-blue-600 dark:text-blue-400 flex items-center gap-1">
            <Lightbulb className="w-3 h-3" />
            Type &quot;yes&quot; or &quot;oui&quot; to confirm, &quot;no&quot; or &quot;non&quot; to cancel
          </div>
        )}
      </div>
    </div>
  )
}
