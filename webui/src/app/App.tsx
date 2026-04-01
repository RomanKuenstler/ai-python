import { useEffect, useState } from "react";
import { BrowserRouter, Navigate, Route, Routes, useLocation, useNavigate, useParams } from "react-router-dom";
import { AdminPage } from "../components/admin/AdminPage";
import { ChatView } from "../components/chat/ChatView";
import { Dialog } from "../components/common/Dialog";
import { ChatFilterDialog } from "../components/filters/ChatFilterDialog";
import { AppShell } from "../components/layout/AppShell";
import { LibraryPage } from "../components/library/LibraryPage";
import { PreferencesDialog } from "../components/preferences/PreferencesDialog";
import { Sidebar } from "../components/sidebar/Sidebar";
import { useChatApp } from "../hooks/useChatApp";
import { LoginPage } from "../pages/LoginPage";
import { PasswordChangePage } from "../pages/PasswordChangePage";

type PreferencesTab = "general" | "personalization" | "settings" | "filter" | "archive";

function AppRoutes() {
  const app = useChatApp();
  const navigate = useNavigate();
  const location = useLocation();
  const activeView = location.pathname.startsWith("/library") ? "library" : location.pathname.startsWith("/admin") ? "admin" : "chat";
  const [preferencesTab, setPreferencesTab] = useState<PreferencesTab | null>(null);
  const [infoOpen, setInfoOpen] = useState(false);
  const [helpOpen, setHelpOpen] = useState(false);
  const [passwordDialogOpen, setPasswordDialogOpen] = useState(false);
  const [chatFilterChatId, setChatFilterChatId] = useState<string | null>(null);

  useEffect(() => {
    if (!app.isAuthenticated || app.requiresPasswordChange || app.bootstrapping || app.chats.length === 0) {
      return;
    }

    const fallbackChatId = app.activeChatId ?? app.chats[0].id;
    const currentChatId = location.pathname.startsWith("/chats/") ? location.pathname.split("/")[2] ?? null : null;

    if (location.pathname === "/" || location.pathname === "/login") {
      navigate(`/chats/${fallbackChatId}`, { replace: true });
      return;
    }

    if (currentChatId && !app.chats.some((chat) => chat.id === currentChatId)) {
      navigate(`/chats/${fallbackChatId}`, { replace: true });
    }
  }, [app.activeChatId, app.bootstrapping, app.chats, app.isAuthenticated, app.requiresPasswordChange, location.pathname, navigate]);

  if (!app.authReady || app.authLoading) {
    return <div className="auth-screen"><div className="auth-card"><p>Loading session...</p></div></div>;
  }

  if (!app.isAuthenticated) {
    return <LoginPage loading={app.authLoading} error={app.authError} onSubmit={(username, password) => app.login(username, password).then(() => undefined)} />;
  }

  if (!app.currentUser) {
    return null;
  }

  if (app.requiresPasswordChange) {
    return (
      <PasswordChangePage
        user={app.currentUser}
        loading={app.passwordChanging}
        error={app.authError}
        onSubmit={(currentPassword, newPassword, confirmPassword) => app.changePassword(currentPassword, newPassword, confirmPassword).then(() => undefined)}
        onLogout={app.logout}
      />
    );
  }

  async function openPreferences(tab: PreferencesTab = "general") {
    setPreferencesTab(tab);
    await Promise.all([app.loadSettings(), app.loadPersonalization()]);
    if (tab === "filter") {
      await app.loadGlobalFilters();
    }
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
      currentUser={app.currentUser}
      onCreateChat={() => void handleCreateChat()}
      onOpenLibrary={() => navigate("/library")}
      onOpenAdmin={() => navigate("/admin")}
      onOpenArchive={() => void openPreferences("archive")}
      onOpenInfo={() => setInfoOpen(true)}
      onOpenHelp={() => setHelpOpen(true)}
      onOpenPreferences={(tab) => void openPreferences(tab ?? "settings")}
      onOpenChangePassword={() => setPasswordDialogOpen(true)}
      onLogout={() => void app.logout()}
      onSelectChat={(chatId) => void handleSelectChat(chatId)}
      onRenameChat={(chatId, chatName) => void handleRenameChat(chatId, chatName)}
      onArchiveChat={(chatId) => void handleArchiveChat(chatId)}
      onOpenChatFilter={(chat) => {
        setChatFilterChatId(chat.id);
        void app.loadChatFilters(chat.id);
      }}
      onDownloadChat={(chatId) => void app.downloadChat(chatId)}
      onDeleteChat={(chatId) => void handleDeleteChat(chatId)}
    />
  );

  return (
    <>
      <AppShell
        sidebar={sidebar}
        assistantMode={app.assistantMode}
        availableModes={app.settings?.available_assistant_modes ?? ["simple", "refine", "thinking"]}
        onAssistantModeChange={app.setAssistantMode}
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
              path="/admin"
              element={
                app.currentUser.role === "admin" ? (
                  <AdminPage
                    currentUser={app.currentUser}
                    users={app.adminUsers}
                    loading={app.adminLoading}
                    error={app.adminError}
                    busyUserIds={app.adminBusyUserIds}
                    onLoad={() => void app.loadAdminUsers()}
                    onCreateUser={(payload) => app.createAdminUser(payload).then(() => undefined)}
                    onUpdateUser={(userId, payload) => app.updateAdminUser(userId, payload).then(() => undefined)}
                    onDeleteUser={(userId) => app.deleteAdminUser(userId).then(() => undefined)}
                  />
                ) : (
                  <Navigate to="/" replace />
                )
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
                  attachmentRules={app.attachmentRules}
                  onOpenChat={(chatId) => void app.ensureChatLoaded(chatId)}
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
          personalizationDraft={app.personalizationDraft}
          availableModes={app.settings?.available_assistant_modes ?? ["simple", "refine", "thinking"]}
          globalFilterTags={app.globalTagFilters}
          loading={app.settingsLoading}
          saving={app.settingsSaving}
          personalizationLoading={app.personalizationLoading}
          personalizationSaving={app.personalizationSaving}
          filterLoading={app.filterLoading}
          filterError={app.filterError}
          filterBusyKeys={app.filterBusyKeys}
          error={app.settingsError}
          success={app.settingsSuccess}
          personalizationError={app.personalizationError}
          personalizationSuccess={app.personalizationSuccess}
          onClose={() => setPreferencesTab(null)}
          onDownloadChat={(chatId) => void app.downloadChat(chatId)}
          onUnarchiveChat={(chatId) => void app.unarchiveChat(chatId)}
          onDeleteChat={(chatId) => void handleDeleteChat(chatId)}
          onFieldChange={app.updateSettingsDraft}
          onPersonalizationFieldChange={app.updatePersonalizationDraft}
          onSaveSettings={() => void app.saveSettings()}
          onSavePersonalization={() => void app.savePersonalization()}
          onOpenFilterTab={() => void app.loadGlobalFilters()}
          onToggleGlobalTag={(tag, isEnabled) => void app.toggleGlobalTagFilter(tag.tag, isEnabled)}
        />
      ) : null}

      {chatFilterChatId ? (
        <ChatFilterDialog
          chatName={app.chats.find((chat) => chat.id === chatFilterChatId)?.chat_name ?? "Chat"}
          files={app.chatFileFiltersByChat[chatFilterChatId] ?? []}
          tags={app.chatTagFiltersByChat[chatFilterChatId] ?? []}
          loading={app.filterLoading && !(app.chatFileFiltersByChat[chatFilterChatId] && app.chatTagFiltersByChat[chatFilterChatId])}
          error={app.filterError}
          busyKeys={app.filterBusyKeys}
          onClose={() => setChatFilterChatId(null)}
          onToggleTag={(tag, isEnabled) => void app.toggleChatTagFilter(chatFilterChatId, tag.tag, isEnabled)}
          onToggleFile={(file, isEnabled) => void app.toggleChatFileFilter(chatFilterChatId, file.file_id, isEnabled)}
        />
      ) : null}

      {passwordDialogOpen ? (
        <Dialog
          title="Change Password"
          onClose={() => setPasswordDialogOpen(false)}
          className="dialog-wide"
          actions={null}
        >
          <PasswordChangePage
            user={app.currentUser}
            loading={app.passwordChanging}
            error={app.authError}
            requiresCurrentPassword
            compact
            showLogout={false}
            onSubmit={async (currentPassword, newPassword, confirmPassword) => {
              await app.changePassword(currentPassword, newPassword, confirmPassword);
              setPasswordDialogOpen(false);
            }}
            onLogout={app.logout}
          />
        </Dialog>
      ) : null}

      {infoOpen ? (
        <Dialog
          title="Info"
          onClose={() => setInfoOpen(false)}
          className="dialog-wide info-dialog"
          actions={null}
        >
          <div className="info-panel">
            <section className="info-panel-section">
              <h4>Status</h4>
              <div className="info-table">
                {[
                  ["Backend", "Web API orchestration, auth, and chat handling."],
                  ["Retriever", "Retrieval, prompt assembly, and answer generation."],
                  ["Embedder", "Processes library files and maintains embeddings."],
                  ["OCR Scanner", "Extracts text from supported images when needed."],
                  ["Vector Db", "Stores nearest-neighbor retrieval vectors."],
                  ["Postgres", "Stores users, chats, file metadata, and settings."],
                ].map(([label, description]) => (
                  <div className="info-row" key={label}>
                    <div className="info-copy">
                      <strong>{label}</strong>
                      <span>{description}</span>
                    </div>
                    <span className="status-pill enabled">Active</span>
                  </div>
                ))}
              </div>
            </section>
          </div>
        </Dialog>
      ) : null}

      {helpOpen ? (
        <Dialog title="Help" onClose={() => setHelpOpen(false)} className="dialog-wide help-dialog" actions={null}>
          <div className="info-panel">
            <section className="info-panel-section">
              <h4>Authentication</h4>
              <p>Sign in with a provisioned user. New or reset users must change the default password before entering the app.</p>
            </section>
            <section className="info-panel-section">
              <h4>Chat Usage</h4>
              <p>Create chats from the sidebar, use one chat per topic when helpful, and open the chat menu to rename, download, archive, or delete a chat.</p>
              <p>Type in the bottom composer and press Enter to send or Shift+Enter for a new line.</p>
            </section>
          </div>
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
  attachmentRules: ReturnType<typeof useChatApp>["attachmentRules"];
  onOpenChat: (chatId: string) => void;
  onSend: ReturnType<typeof useChatApp>["sendMessage"];
};

function ChatRoute({
  messages,
  loading,
  sending,
  error,
  assistantMode,
  attachmentRules,
  onOpenChat,
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
      attachmentRules={attachmentRules}
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
