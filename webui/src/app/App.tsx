import { useEffect } from "react";
import { BrowserRouter, Navigate, Route, Routes, useLocation, useNavigate, useParams } from "react-router-dom";
import { ChatView } from "../components/chat/ChatView";
import { AppShell } from "../components/layout/AppShell";
import { LibraryPage } from "../components/library/LibraryPage";
import { Sidebar } from "../components/sidebar/Sidebar";
import { useChatApp } from "../hooks/useChatApp";

function AppRoutes() {
  const app = useChatApp();
  const navigate = useNavigate();
  const location = useLocation();
  const activeView = location.pathname.startsWith("/library") ? "library" : "chat";

  useEffect(() => {
    if (app.bootstrapping || app.chats.length === 0) {
      return;
    }

    if (location.pathname === "/") {
      navigate(`/chats/${app.activeChatId ?? app.chats[0].id}`, { replace: true });
    }
  }, [app.activeChatId, app.bootstrapping, app.chats, location.pathname, navigate]);

  async function handleCreateChat() {
    const chat = await app.createChat();
    navigate(`/chats/${chat.id}`);
  }

  async function handleSelectChat(chatId: string) {
    await app.ensureChatLoaded(chatId);
    navigate(`/chats/${chatId}`);
  }

  async function handleRenameChat(chatId: string, chatName: string) {
    await app.renameChat(chatId, chatName);
  }

  async function handleDeleteChat(chatId: string) {
    const fallbackChatId = await app.deleteChat(chatId);
    navigate(`/chats/${fallbackChatId}`);
  }

  const sidebar = (
    <Sidebar
      chats={app.chats}
      activeChatId={app.activeChatId}
      activeView={activeView}
      onCreateChat={() => void handleCreateChat()}
      onOpenLibrary={() => navigate("/library")}
      onSelectChat={(chatId) => void handleSelectChat(chatId)}
      onRenameChat={(chatId, chatName) => void handleRenameChat(chatId, chatName)}
      onDeleteChat={(chatId) => void handleDeleteChat(chatId)}
    />
  );

  return (
    <AppShell
      sidebar={sidebar}
      content={
        <Routes>
          <Route
            path="/library"
            element={
              <LibraryPage
                library={app.library}
                loading={app.libraryLoading}
                error={app.libraryError}
                uploading={app.uploading}
                busyFileIds={app.busyFileIds}
                onLoad={() => void app.loadLibrary()}
                onToggleFile={(file) => void app.toggleLibraryFile(file)}
                onDeleteFile={(fileId) => void app.deleteLibraryFile(fileId)}
                onUploadFiles={(files, tagsByFile) => app.uploadLibraryFiles(files, tagsByFile)}
              />
            }
          />
          <Route
            path="/chats/:chatId"
            element={
              <ChatRoute
                loading={app.loadingMessages}
                error={app.appError}
                messages={app.activeMessages}
                sending={app.sending}
                onOpenChat={(chatId) => void app.ensureChatLoaded(chatId)}
                onSend={app.sendMessage}
              />
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      }
    />
  );
}

type ChatRouteProps = {
  messages: ReturnType<typeof useChatApp>["activeMessages"];
  loading: boolean;
  sending: boolean;
  error: string | null;
  onOpenChat: (chatId: string) => void;
  onSend: (value: string) => Promise<void>;
};

function ChatRoute({ messages, loading, sending, error, onOpenChat, onSend }: ChatRouteProps) {
  const { chatId } = useParams();

  useEffect(() => {
    if (chatId) {
      onOpenChat(chatId);
    }
  }, [chatId, onOpenChat]);

  return <ChatView messages={messages} sending={sending} loadingMessages={loading} error={error} onSend={onSend} />;
}

export function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}
