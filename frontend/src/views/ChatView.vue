<template>
  <div class="min-h-screen bg-neutral-50 dark:bg-neutral-900 transition-colors duration-300">
    <!-- Header -->
    <header class="glass sticky top-0 z-10 border-b border-neutral-200/50 dark:border-neutral-700/50">
      <div class="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 gradient-primary rounded-full flex items-center justify-center shadow-lg">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
            </svg>
          </div>
          <div>
            <h1 class="text-xl font-semibold text-neutral-900 dark:text-neutral-100 text-balance">Customer Support</h1>
            <p class="text-sm text-neutral-500 dark:text-neutral-400">AI Assistant</p>
          </div>
        </div>
        
        <div class="flex items-center space-x-2">
          <button
            @click="themeStore.toggleTheme"
            class="btn-secondary p-2 rounded-xl"
            title="Toggle theme"
          >
            <svg v-if="themeStore.isDarkMode" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path>
            </svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path>
            </svg>
          </button>
          
          <button
            @click="chatStore.clearMessages"
            class="btn-secondary p-2 rounded-xl"
            title="Clear conversation"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
            </svg>
          </button>
        </div>
      </div>
    </header>

    <!-- Main Chat Area -->
    <main class="max-w-4xl mx-auto px-4 py-6 flex flex-col h-[calc(100vh-88px)]">
      <!-- Welcome Message -->
      <div v-if="chatStore.messages.length === 0" class="flex-1 flex items-center justify-center fade-in">
        <div class="text-center max-w-md">
          <div class="w-20 h-20 gradient-primary rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-xl animate-bounce-subtle">
            <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
            </svg>
          </div>
          <h2 class="text-3xl font-bold text-neutral-900 dark:text-neutral-100 mb-3 text-balance">Welcome to Customer Support</h2>
          <p class="text-neutral-600 dark:text-neutral-400 mb-8 text-pretty leading-relaxed">How can I help you today? Ask me anything about our products or services.</p>
          
          <!-- Quick Actions -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <button
              v-for="action in quickActions"
              :key="action.text"
              @click="sendQuickAction(action.text)"
              class="card p-4 text-left hover:shadow-md hover:scale-[1.02] transition-all duration-200 group"
            >
              <div class="flex items-center space-x-3">
                <span class="text-2xl group-hover:scale-110 transition-transform duration-200">{{ action.icon }}</span>
                <span class="text-sm font-medium text-neutral-900 dark:text-neutral-100 text-pretty">{{ action.text }}</span>
              </div>
            </button>
          </div>
        </div>
      </div>

      <!-- Messages -->
      <div v-else class="flex-1 overflow-y-auto space-y-4 mb-6 scroll-smooth" ref="messagesContainer">
        <TransitionGroup name="message" tag="div">
          <div
            v-for="message in chatStore.messages"
            :key="message.timestamp?.getTime() || Math.random()"
            :class="[
              'flex',
              message.sender === 'user' ? 'justify-end' : 'justify-start'
            ]"
          >
            <div
              :class="[
                'max-w-xs sm:max-w-md lg:max-w-lg xl:max-w-xl px-4 py-3 rounded-2xl shadow-sm',
                message.sender === 'user'
                  ? 'gradient-primary text-white rounded-br-md shadow-primary-500/20'
                  : 'card rounded-bl-md'
              ]"
            >
              <div v-if="message.sender === 'bot'" v-html="formatMessage(message.content)" class="prose-chat"></div>
              <div v-else class="text-pretty">{{ message.content }}</div>
              <div
                :class="[
                  'text-xs mt-2 opacity-70 font-medium',
                  message.sender === 'user' ? 'text-primary-100' : 'text-neutral-500 dark:text-neutral-400'
                ]"
              >
                {{ formatTime(message.timestamp) }}
              </div>
            </div>
          </div>
        </TransitionGroup>

        <!-- Typing Indicator -->
        <div v-if="chatStore.isTyping" class="flex justify-start slide-up">
          <div class="card px-4 py-3 rounded-2xl rounded-bl-md">
            <div class="flex space-x-1">
              <div class="w-2 h-2 bg-neutral-400 rounded-full animate-bounce"></div>
              <div class="w-2 h-2 bg-neutral-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
              <div class="w-2 h-2 bg-neutral-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="card p-4 shadow-lg">
        <form @submit.prevent="sendMessage" class="flex space-x-3">
          <input
            v-model="messageInput"
            type="text"
            placeholder="Type your message..."
            :disabled="chatStore.isLoading"
            class="flex-1 bg-transparent border-none outline-none text-neutral-900 dark:text-neutral-100 placeholder-neutral-500 dark:placeholder-neutral-400 text-pretty"
          />
          <button
            type="submit"
            :disabled="!messageInput.trim() || chatStore.isLoading"
            class="p-3 gradient-primary hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl transition-all duration-200 disabled:hover:shadow-none"
          >
            <svg v-if="chatStore.isLoading" class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
            </svg>
          </button>
        </form>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { useChatStore } from '../stores/chat'
import { useThemeStore } from '../stores/theme'
import { marked } from 'marked'
import { format } from 'date-fns'

const chatStore = useChatStore()
const themeStore = useThemeStore()
const messageInput = ref('')
const messagesContainer = ref<HTMLElement>()

const quickActions = [
  { icon: '🔑', text: 'How can I reset my password?' },
  { icon: '🏃🏽‍♂️‍➡️', text: 'Help with my schedule' },
  { icon: '👨🏼‍⚕️', text: 'How can I improve my mental health?' },
  { icon: '📦', text: 'Track my order' },
  { icon: '💳', text: 'I have a billing question' },
  { icon: '🔧', text: 'Technical support needed' },
]

const sendMessage = async () => {
  if (!messageInput.value.trim()) return
  
  const message = messageInput.value
  messageInput.value = ''
  
  await chatStore.sendMessage(message)
  scrollToBottom()
}

const sendQuickAction = async (text: string) => {
  await chatStore.sendMessage(text)
  scrollToBottom()
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const formatMessage = (content: string) => {
  return marked(content)
}

const formatTime = (timestamp: Date | undefined) => {
  if (!timestamp) return ''
  return format(timestamp, 'HH:mm')
}

// Watch for new messages and scroll to bottom
watch(() => chatStore.messages.length, () => {
  scrollToBottom()
})

onMounted(() => {
  themeStore.initTheme()
})
</script>

<style scoped>
.message-enter-active {
  transition: all 0.3s ease-out;
}

.message-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
</style>