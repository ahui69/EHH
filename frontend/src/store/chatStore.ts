import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Conversation, Message, Settings } from '../types';
import { conversationAPI } from '../services/api';

interface ChatState {
  conversations: Conversation[];
  currentConversationId: string | null;
  settings: Settings;
  isLoading: boolean;
  isSyncing: boolean;
  addConversation: (conversation: Conversation) => void;
  deleteConversation: (id: string) => void;
  setCurrentConversation: (id: string) => void;
  addMessage: (conversationId: string, message: Message) => void;
  updateSettings: (settings: Partial<Settings>) => void;
  exportConversations: () => string;
  importConversations: (data: string) => void;
  clearAll: () => void;
  syncWithBackend: () => Promise<void>;
  loadConversationFromBackend: (conversationId: string) => Promise<void>;
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      conversations: [],
      currentConversationId: null,
      isLoading: false,
      isSyncing: false,
      settings: {
        theme: typeof window !== 'undefined' && window.matchMedia 
          ? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
          : 'dark',
        temperature: 0.7,
        maxTokens: 2000,
        model: 'gpt-4-turbo-preview',
        useMemory: true,
        useResearch: true,
        autoLearn: true,
      },
      addConversation: (conversation) =>
        set((state) => ({
          conversations: [conversation, ...state.conversations],
          currentConversationId: conversation.id,
        })),
      deleteConversation: (id) =>
        set((state) => ({
          conversations: state.conversations.filter((c) => c.id !== id),
          currentConversationId:
            state.currentConversationId === id ? state.conversations[0]?.id || null : state.currentConversationId,
        })),
      setCurrentConversation: (id) => set({ currentConversationId: id }),
      addMessage: (conversationId, message) =>
        set((state) => ({
          conversations: state.conversations.map((c) =>
            c.id === conversationId
              ? { ...c, messages: [...c.messages, message], updatedAt: Date.now(), title: c.messages.length === 0 ? message.content.slice(0, 50) : c.title }
              : c
          ),
        })),
      updateSettings: (newSettings) =>
        set((state) => {
          const updated = { ...state.settings, ...newSettings };
          // Persist theme to localStorage separately for instant load
          if (newSettings.theme && typeof window !== 'undefined') {
            localStorage.setItem('mordzix-theme', newSettings.theme);
            document.documentElement.classList.toggle('dark', newSettings.theme === 'dark');
          }
          return { settings: updated };
        }),
      exportConversations: () => JSON.stringify({ conversations: get().conversations, settings: get().settings, exportedAt: Date.now() }),
      importConversations: (data) => {
        try {
          const parsed = JSON.parse(data);
          set({ conversations: parsed.conversations || [], settings: parsed.settings || get().settings });
        } catch (error) {
          console.error('Import failed:', error);
        }
      },
      clearAll: () => set({ conversations: [], currentConversationId: null }),
      
      // Sync with backend - load all conversations from /api/memory/conversations
      syncWithBackend: async () => {
        set({ isSyncing: true });
        try {
          const response = await conversationAPI.listConversations(100, 0);
          if (response.success && response.data?.conversations) {
            const backendConversations: Conversation[] = response.data.conversations.map((conv: any) => ({
              id: conv.id,
              title: conv.title || 'Untitled',
              messages: [], // Will be loaded on demand
              createdAt: conv.created_at || Date.now(),
              updatedAt: conv.updated_at || Date.now(),
            }));
            
            // Merge with local conversations (prefer backend)
            const merged = [
              ...backendConversations,
              ...get().conversations.filter(c => !backendConversations.find(bc => bc.id === c.id))
            ];
            
            set({ conversations: merged, isSyncing: false });
          }
        } catch (error) {
          console.error('Sync failed:', error);
          set({ isSyncing: false });
        }
      },
      
      // Load full conversation messages from backend
      loadConversationFromBackend: async (conversationId: string) => {
        set({ isLoading: true });
        try {
          const response = await conversationAPI.getConversation(conversationId);
          if (response.success && response.data?.messages) {
            const messages: Message[] = response.data.messages.map((msg: any) => ({
              id: `${msg.timestamp}-${msg.role}`,
              role: msg.role,
              content: msg.content,
              timestamp: msg.timestamp,
            }));
            
            set((state) => ({
              conversations: state.conversations.map(c =>
                c.id === conversationId ? { ...c, messages } : c
              ),
              isLoading: false
            }));
          }
        } catch (error) {
          console.error('Load conversation failed:', error);
          set({ isLoading: false });
        }
      },
    }),
    { name: 'mordzix-chat-storage' }
  )
);
