import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export interface Message {
  id?: number
  content: string
  sender: 'user' | 'bot'
  timestamp: Date
}

export interface Conversation {
  id: string
  messages: Message[]
  created_at: Date
  updated_at: Date
}

const API_BASE_URL = 'http://127.0.0.1:8000/api'

export const useChatStore = defineStore('chat', () => {
  const messages = ref<Message[]>([])
  const sessionId = ref<string | null>(null)
  const isLoading = ref(false)
  const isTyping = ref(false)

  const lastMessage = computed(() => {
    return messages.value[messages.value.length - 1]
  })

  const addMessage = (message: Message) => {
    messages.value.push({
      ...message,
      timestamp: new Date()
    })
  }

  const sendMessage = async (content: string) => {
    if (!content.trim()) return

    // Add user message
    addMessage({
      content: content.trim(),
      sender: 'user',
      timestamp: new Date()
    })

    isLoading.value = true
    isTyping.value = true

    try {
      const response = await axios.post(`${API_BASE_URL}/chat/`, {
        message: content.trim(),
        session_id: sessionId.value
      }, {
        headers: {
          'Content-Type': 'application/json',
        },
        withCredentials: false
      })

      // Update session ID if new
      if (response.data.session_id && !sessionId.value) {
        sessionId.value = response.data.session_id
      }

      // Add bot response
      addMessage({
        content: response.data.response,
        sender: 'bot',
        timestamp: new Date()
      })

    } catch (error) {
      console.error('Error sending message:', error)
      
      // More detailed error handling
      if (axios.isAxiosError(error)) {
        if (error.response) {
          console.error('Response error:', error.response.data)
          console.error('Status:', error.response.status)
        } else if (error.request) {
          console.error('Request error:', error.request)
        }
      }
      
      addMessage({
        content: 'Sorry, I encountered an error. Please try again. Make sure the backend server is running on http://127.0.0.1:8000/',
        sender: 'bot',
        timestamp: new Date()
      })
    } finally {
      isLoading.value = false
      isTyping.value = false
    }
  }

  const loadConversation = async (sessionId: string) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/conversation/${sessionId}/`, {
        withCredentials: false
      })
      messages.value = response.data.messages.map((msg: any) => ({
        ...msg,
        timestamp: new Date(msg.timestamp)
      }))
    } catch (error) {
      console.error('Error loading conversation:', error)
    }
  }

  const clearMessages = () => {
    messages.value = []
    sessionId.value = null
  }

  const createSupportTicket = async (subject: string, description: string) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/ticket/create/`, {
        session_id: sessionId.value,
        subject,
        description
      }, {
        headers: {
          'Content-Type': 'application/json',
        },
        withCredentials: false
      })
      return response.data
    } catch (error) {
      console.error('Error creating support ticket:', error)
      throw error
    }
  }

  return {
    messages,
    sessionId,
    isLoading,
    isTyping,
    lastMessage,
    addMessage,
    sendMessage,
    loadConversation,
    clearMessages,
    createSupportTicket
  }
})