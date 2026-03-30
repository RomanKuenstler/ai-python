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

  return (
    <AppShell
      onOpenArchive={() => undefined}
      onOpenPreferences={() => undefined}
      sidebar={
        <Sidebar
          chats={chats}
          activeChatId={activeChatId}
          activeView="chat"
          onCreateChat={() => void createChat()}
          onOpenLibrary={() => undefined}
          onOpenArchive={() => undefined}
          onOpenInfo={() => undefined}
          onOpenHelp={() => undefined}
          onOpenPreferences={() => undefined}
          onSelectChat={(chatId) => void ensureChatLoaded(chatId)}
          onRenameChat={(chatId, chatName) => void renameChat(chatId, chatName)}
          onArchiveChat={(chatId) => void archiveChat(chatId)}
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
          availableModes={settings?.available_assistant_modes ?? ["simple", "refine"]}
          attachmentRules={attachmentRules}
          onAssistantModeChange={setAssistantMode}
          onSend={sendMessage}
        />
      }
    />
  );
}
