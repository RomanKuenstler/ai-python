import { AppShell } from "../components/layout/AppShell";
import { Sidebar } from "../components/sidebar/Sidebar";
import { ChatView } from "../components/chat/ChatView";
import { useChatApp } from "../hooks/useChatApp";

export function ChatPage() {
  const {
    currentUser,
    chats,
    activeChatId,
    activeMessages,
    loadingMessages,
    sending,
    appError,
    assistantMode,
    settings,
    attachmentRules,
    createChat,
    ensureChatLoaded,
    renameChat,
    archiveChat,
    downloadChat,
    deleteChat,
    setAssistantMode,
    sendMessage,
  } = useChatApp();

  if (!currentUser) {
    return null;
  }

  return (
    <AppShell
      assistantMode={assistantMode}
      availableModes={settings?.available_assistant_modes ?? ["simple", "refine", "thinking"]}
      onAssistantModeChange={setAssistantMode}
      sidebar={
        <Sidebar
          chats={chats}
          activeChatId={activeChatId}
          activeView="chat"
          currentUser={currentUser}
          onCreateChat={() => void createChat()}
          onOpenLibrary={() => undefined}
          onOpenAdmin={() => undefined}
          onOpenArchive={() => undefined}
          onOpenInfo={() => undefined}
          onOpenHelp={() => undefined}
          onOpenPreferences={() => undefined}
          onOpenChangePassword={() => undefined}
          onLogout={() => undefined}
          onSelectChat={(chatId) => void ensureChatLoaded(chatId)}
          onRenameChat={(chatId, chatName) => void renameChat(chatId, chatName)}
          onArchiveChat={(chatId) => void archiveChat(chatId)}
          onOpenChatFilter={() => undefined}
          onDownloadChat={(chatId) => void downloadChat(chatId)}
          onDeleteChat={(chatId) => void deleteChat(chatId)}
        />
      }
      content={
        <ChatView
          messages={activeMessages}
          sending={sending}
          loadingMessages={loadingMessages}
          error={appError}
          assistantMode={assistantMode}
          attachmentRules={attachmentRules}
          onSend={sendMessage}
        />
      }
    />
  );
}
