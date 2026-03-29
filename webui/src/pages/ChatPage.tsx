import { AppShell } from "../components/layout/AppShell";
import { Sidebar } from "../components/sidebar/Sidebar";
import { ChatView } from "../components/chat/ChatView";
import { useChatApp } from "../hooks/useChatApp";

export function ChatPage() {
  const { chats, activeChatId, activeMessages, loadingMessages, sending, appError, createChat, selectChat, sendMessage } =
    useChatApp();

  return (
    <AppShell
      sidebar={<Sidebar chats={chats} activeChatId={activeChatId} onCreateChat={() => void createChat()} onSelectChat={(chatId) => void selectChat(chatId)} />}
      content={
        <ChatView
          messages={activeMessages}
          sending={sending}
          loadingMessages={loadingMessages}
          error={appError}
          onSend={sendMessage}
        />
      }
    />
  );
}
