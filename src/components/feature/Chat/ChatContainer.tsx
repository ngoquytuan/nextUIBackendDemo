// src/components/feature/Chat/ChatContainer.tsx
'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { chatAPI, API_BASE_URL } from '@/lib/api/client'

interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
  sources?: any[]
}

export function ChatContainer() {
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [conversationId, setConversationId] = useState<string>()
  const [connectionStatus, setConnectionStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking')
  const [isClient, setIsClient] = useState(false) // Fix hydration

  // Fix hydration mismatch
  useEffect(() => {
    setIsClient(true)
    // Initialize messages after client-side hydration
    setMessages([
      { 
        id: '1', 
        content: 'Hello! I\'m your RAG assistant. Upload documents and ask me questions!', 
        role: 'assistant',
        timestamp: new Date()
      }
    ])
    checkBackendConnection()
  }, [])

  const checkBackendConnection = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`)
      if (response.ok) {
        setConnectionStatus('connected')
        console.log('✅ Backend connected')
      } else {
        setConnectionStatus('disconnected')
      }
    } catch (error) {
      setConnectionStatus('disconnected')
      console.error('❌ Backend connection failed:', error)
    }
  }

  const handleSend = async () => {
    if (!message.trim()) return
    
    const userMessage: Message = {
      id: Date.now().toString(),
      content: message,
      role: 'user',
      timestamp: new Date()
    }
    
    setMessages(prev => [...prev, userMessage])
    setMessage('')
    setIsLoading(true)
    
    try {
      const response = await chatAPI.sendMessage(message, conversationId)
      
      const assistantMessage: Message = {
        id: response.id,
        content: response.content,
        role: 'assistant',
        timestamp: new Date(response.timestamp),
        sources: response.sources
      }
      
      setMessages(prev => [...prev, assistantMessage])
      
      // Set conversation ID if first message
      if (!conversationId) {
        setConversationId(response.conversation_id)
      }
      
    } catch (error) {
      console.error('Chat error:', error)
      
      // Add error message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: `❌ Error: ${error instanceof Error ? error.message : 'Failed to send message'}. Please check if the backend is running.`,
        role: 'assistant',
        timestamp: new Date()
      }
      
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const clearChat = () => {
    setMessages([
      { 
        id: '1', 
        content: 'Hello! I\'m your RAG assistant. Upload documents and ask me questions!', 
        role: 'assistant',
        timestamp: new Date()
      }
    ])
    setConversationId(undefined)
  }

  const formatTime = (timestamp: Date) => {
    // Fix hydration by consistent formatting
    if (!isClient) return ''
    return timestamp.toLocaleTimeString()
  }

  // Show loading state during hydration
  if (!isClient) {
    return (
      <div className="flex flex-col h-full">
        <div className="flex items-center justify-between p-4 border-b bg-muted/30">
          <div className="flex items-center space-x-2">
            <h3 className="font-medium">Chat Assistant</h3>
            <div className="w-2 h-2 rounded-full bg-yellow-500" />
            <span className="text-xs text-muted-foreground">Loading...</span>
          </div>
        </div>
        <Card className="flex-1 flex flex-col m-4">
          <div className="flex-1 flex items-center justify-center">
            <div className="text-muted-foreground">Loading chat...</div>
          </div>
        </Card>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header with connection status */}
      <div className="flex items-center justify-between p-4 border-b bg-muted/30">
        <div className="flex items-center space-x-2">
          <h3 className="font-medium">Chat Assistant</h3>
          <div className={`w-2 h-2 rounded-full ${
            connectionStatus === 'connected' ? 'bg-green-500' : 
            connectionStatus === 'checking' ? 'bg-yellow-500' : 'bg-red-500'
          }`} />
          <span className="text-xs text-muted-foreground">
            {connectionStatus === 'connected' ? 'Connected' : 
             connectionStatus === 'checking' ? 'Connecting...' : 'Disconnected'}
          </span>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={checkBackendConnection}
            disabled={connectionStatus === 'checking'}
          >
            🔄 Refresh
          </Button>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={clearChat}
          >
            🗑️ Clear
          </Button>
        </div>
      </div>

      {/* Chat messages */}
      <Card className="flex-1 flex flex-col m-4">
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] p-3 rounded-lg ${
                msg.role === 'user' 
                  ? 'bg-primary text-primary-foreground' 
                  : 'bg-muted text-muted-foreground'
              }`}>
                <div className="whitespace-pre-wrap">{msg.content}</div>
                
                {/* Show sources if available */}
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-current/20">
                    <div className="text-xs opacity-75">Sources:</div>
                    {msg.sources.map((source, idx) => (
                      <div key={idx} className="text-xs opacity-75">
                        📄 {source.filename} (Score: {source.relevance_score})
                      </div>
                    ))}
                  </div>
                )}
                
                <div className="text-xs opacity-50 mt-1">
                  {formatTime(msg.timestamp)}
                </div>
              </div>
            </div>
          ))}
          
          {/* Loading indicator */}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-muted p-3 rounded-lg">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-current rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-current rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                  <div className="w-2 h-2 bg-current rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                  <span className="text-sm">Thinking...</span>
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Input area */}
        <div className="border-t p-4">
          <div className="flex space-x-2">
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              className="flex-1 px-3 py-2 border rounded-md bg-background text-foreground resize-none min-h-[40px] max-h-[120px]"
              placeholder={
                connectionStatus === 'connected' 
                  ? "Ask about your documents... (Enter to send, Shift+Enter for new line)"
                  : "Backend disconnected. Please check connection."
              }
              disabled={isLoading || connectionStatus !== 'connected'}
              rows={1}
            />
            <Button 
              onClick={handleSend} 
              disabled={!message.trim() || isLoading || connectionStatus !== 'connected'}
            >
              {isLoading ? '⏳' : '📤'} Send
            </Button>
          </div>
          
          {/* Debug info */}
          <div className="mt-2 text-xs text-muted-foreground">
            <div className="flex items-center space-x-4">
              <div>
                🔗 Backend: {API_BASE_URL}
              </div>
              {conversationId && (
                <div>
                  💬 Conversation: {conversationId.slice(0, 8)}...
                </div>
              )}
              <div>
                📊 Messages: {messages.length}
              </div>
            </div>
          </div>
        </div>
      </Card>
    </div>
  )
}