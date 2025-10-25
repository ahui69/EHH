import { useEffect } from 'react';
import { useChatStore } from './store/chatStore';
import { useAuth } from './contexts/AuthContext';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import SettingsPanel from './components/SettingsPanel';
import Login from './components/Login';

export default function App() {
  const { settings, currentConversationId, addConversation } = useChatStore();
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (settings.theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [settings.theme]);

  // Auto-create first conversation if none exists
  useEffect(() => {
    if (isAuthenticated && !currentConversationId) {
      addConversation({
        id: Date.now().toString(),
        title: 'New Chat',
        messages: [],
        createdAt: Date.now(),
        updatedAt: Date.now(),
      });
    }
  }, [isAuthenticated, currentConversationId]);

  // Show loading spinner during auth check
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-900">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  // Show login if not authenticated
  if (!isAuthenticated) {
    return <Login />;
  }

  return (
    <div className="flex h-screen bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 overflow-hidden">
      <Sidebar />
      <ChatArea />
      <SettingsPanel />
    </div>
  );
}
