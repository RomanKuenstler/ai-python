import { AppShell } from "../components/layout/AppShell";
import { Sidebar } from "../components/sidebar/Sidebar";
import { ChatView } from "../components/chat/ChatView";
import { useChatApp } from "../hooks/useChatApp";

export function ChatPage() {
  const {
    chats,
    activeChatId,
    activeMessages,
    loadingMessages,
    sending,
    appError,
    attachmentRules,
    createChat,
    ensureChatLoaded,
    renameChat,
    deleteChat,
  } = useChatApp();

  return (
    <AppShell
      sidebar={
        <Sidebar
          chats={chats}
          activeChatId={activeChatId}
          activeView="chat"
          onCreateChat={() => void createChat()}
          onOpenLibrary={() => undefined}
          onSelectChat={(chatId) => void ensureChatLoaded(chatId)}
          onRenameChat={(chatId, chatName) => void renameChat(chatId, chatName)}
          onDeleteChat={(chatId) => void deleteChat(chatId)}
        />
      }
      content={
        <ChatView
          messages={activeMessages}
          sending={sending}
          loadingMessages={loadingMessages}
          error={appError}
          attachmentRules={attachmentRules}
          onSend={async () => undefined}
        />
      }
    />
  );
}
