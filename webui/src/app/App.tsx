import { useEffect, useState } from "react";
import { BrowserRouter, Navigate, Route, Routes, useLocation, useNavigate, useParams } from "react-router-dom";
import { ChatView } from "../components/chat/ChatView";
import { Dialog } from "../components/common/Dialog";
import { AppShell } from "../components/layout/AppShell";
import { LibraryPage } from "../components/library/LibraryPage";
import { PreferencesDialog } from "../components/preferences/PreferencesDialog";
import { Sidebar } from "../components/sidebar/Sidebar";
import { useChatApp } from "../hooks/useChatApp";
import type { AssistantMode } from "../types/chat";

type PreferencesTab = "general" | "personalization" | "settings" | "archive";

function AppRoutes() {
  const app = useChatApp();
  const navigate = useNavigate();
  const location = useLocation();
  const activeView = location.pathname.startsWith("/library") ? "library" : "chat";
  const [preferencesTab, setPreferencesTab] = useState<PreferencesTab | null>(null);
  const [infoOpen, setInfoOpen] = useState(false);
  const [helpOpen, setHelpOpen] = useState(false);

  useEffect(() => {
    if (app.bootstrapping || app.chats.length === 0) {
      return;
    }

    if (location.pathname === "/") {
      navigate(`/chats/${app.activeChatId ?? app.chats[0].id}`, { replace: true });
    }
  }, [app.activeChatId, app.bootstrapping, app.chats, location.pathname, navigate]);

  async function openPreferences(tab: PreferencesTab = "general") {
    setPreferencesTab(tab);
    await app.loadSettings();
  }

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

  async function handleArchiveChat(chatId: string) {
    const fallbackChatId = await app.archiveChat(chatId);
    if (fallbackChatId) {
      navigate(`/chats/${fallbackChatId}`);
      return;
    }
    navigate("/");
  }

  async function handleDeleteChat(chatId: string) {
    const fallbackChatId = await app.deleteChat(chatId);
    if (fallbackChatId) {
      navigate(`/chats/${fallbackChatId}`);
      return;
    }
    navigate("/");
  }

  const sidebar = (
    <Sidebar
      chats={app.chats}
      activeChatId={app.activeChatId}
      activeView={activeView}
      onCreateChat={() => void handleCreateChat()}
      onOpenLibrary={() => navigate("/library")}
      onOpenArchive={() => void openPreferences("archive")}
      onOpenInfo={() => setInfoOpen(true)}
      onOpenHelp={() => setHelpOpen(true)}
      onOpenPreferences={(tab) => void openPreferences(tab ?? "settings")}
      onSelectChat={(chatId) => void handleSelectChat(chatId)}
      onRenameChat={(chatId, chatName) => void handleRenameChat(chatId, chatName)}
      onArchiveChat={(chatId) => void handleArchiveChat(chatId)}
      onDownloadChat={(chatId) => void app.downloadChat(chatId)}
      onDeleteChat={(chatId) => void handleDeleteChat(chatId)}
    />
  );

  return (
    <>
      <AppShell
        sidebar={sidebar}
        onOpenArchive={() => void openPreferences("archive")}
        onOpenPreferences={() => void openPreferences("settings")}
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
                  assistantMode={app.assistantMode}
                  availableModes={app.settings?.available_assistant_modes ?? ["simple", "refine"]}
                  attachmentRules={app.attachmentRules}
                  onOpenChat={(chatId) => void app.ensureChatLoaded(chatId)}
                  onAssistantModeChange={app.setAssistantMode}
                  onSend={app.sendMessage}
                />
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        }
      />

      {preferencesTab ? (
        <PreferencesDialog
          initialTab={preferencesTab}
          archivedChats={app.archivedChats}
          settingsDraft={app.settingsDraft}
          availableModes={app.settings?.available_assistant_modes ?? ["simple", "refine"]}
          loading={app.settingsLoading}
          saving={app.settingsSaving}
          error={app.settingsError}
          success={app.settingsSuccess}
          onClose={() => setPreferencesTab(null)}
          onDownloadChat={(chatId) => void app.downloadChat(chatId)}
          onUnarchiveChat={(chatId) => void app.unarchiveChat(chatId)}
          onDeleteChat={(chatId) => void handleDeleteChat(chatId)}
          onFieldChange={app.updateSettingsDraft}
          onSaveSettings={() => void app.saveSettings()}
        />
      ) : null}

      {infoOpen ? (
        <Dialog
          title="Info"
          onClose={() => setInfoOpen(false)}
          actions={
            <button className="secondary-button" type="button" onClick={() => setInfoOpen(false)}>
              Close
            </button>
          }
        >
          <p>This local RAG system indexes your documents, retrieves relevant chunks, and answers with source-backed responses.</p>
        </Dialog>
      ) : null}

      {helpOpen ? (
        <Dialog
          title="Help"
          onClose={() => setHelpOpen(false)}
          actions={
            <button className="secondary-button" type="button" onClick={() => setHelpOpen(false)}>
              Close
            </button>
          }
        >
          <p>Use the library to manage files, choose an assistant mode in the composer, and open preferences to tune retrieval or manage archived chats.</p>
        </Dialog>
      ) : null}

    </>
  );
}

type ChatRouteProps = {
  messages: ReturnType<typeof useChatApp>["activeMessages"];
  loading: boolean;
  sending: boolean;
  error: string | null;
  assistantMode: ReturnType<typeof useChatApp>["assistantMode"];
  availableModes: AssistantMode[];
  attachmentRules: ReturnType<typeof useChatApp>["attachmentRules"];
  onOpenChat: (chatId: string) => void;
  onAssistantModeChange: ReturnType<typeof useChatApp>["setAssistantMode"];
  onSend: ReturnType<typeof useChatApp>["sendMessage"];
};

function ChatRoute({
  messages,
  loading,
  sending,
  error,
  assistantMode,
  availableModes,
  attachmentRules,
  onOpenChat,
  onAssistantModeChange,
  onSend,
}: ChatRouteProps) {
  const { chatId } = useParams();

  useEffect(() => {
    if (chatId) {
      onOpenChat(chatId);
    }
  }, [chatId, onOpenChat]);

  return (
    <ChatView
      messages={messages}
      sending={sending}
      loadingMessages={loading}
      error={error}
      assistantMode={assistantMode}
      availableModes={availableModes}
      attachmentRules={attachmentRules}
      onAssistantModeChange={onAssistantModeChange}
      onSend={onSend}
    />
  );
}

export function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}
