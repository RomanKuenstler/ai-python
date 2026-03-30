import { useEffect, useMemo, useState } from "react";
import { apiClient } from "../api/client";
import type {
  AssistantMode,
  AttachmentMeta,
  Chat,
  LibraryFile,
  LibraryResponse,
  Message,
  Settings,
  SettingsUpdate,
} from "../types/chat";

const ACTIVE_CHAT_STORAGE_KEY = "local-rag-active-chat";

export const ATTACHMENT_MAX_FILES = 3;
export const ATTACHMENT_ALLOWED_EXTENSIONS = [".txt", ".md", ".html", ".htm", ".pdf", ".epub", ".csv", ".png", ".jpg", ".jpeg", ".webp"];

function createOptimisticMessage(
  chatId: string,
  role: "user" | "assistant",
  content: string,
  status: Message["status"],
  attachments: AttachmentMeta[] = [],
): Message {
  return {
    id: `temp-${role}-${crypto.randomUUID()}`,
    chat_id: chatId,
    role,
    content,
    status,
    has_attachments: attachments.length > 0,
    created_at: new Date().toISOString(),
    sources: [],
    attachments,
  };
}

function sortChats(chats: Chat[]) {
  return [...chats].sort((left, right) => right.updated_at.localeCompare(left.updated_at));
}

function triggerJsonDownload(fileName: string, data: unknown) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = fileName;
  anchor.click();
  URL.revokeObjectURL(url);
}

export function useChatApp() {
  const [bootstrapping, setBootstrapping] = useState(true);
  const [chats, setChats] = useState<Chat[]>([]);
  const [archivedChats, setArchivedChats] = useState<Chat[]>([]);
  const [messagesByChat, setMessagesByChat] = useState<Record<string, Message[]>>({});
  const [activeChatId, setActiveChatId] = useState<string | null>(null);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [sending, setSending] = useState(false);
  const [appError, setAppError] = useState<string | null>(null);
  const [library, setLibrary] = useState<LibraryResponse | null>(null);
  const [libraryLoading, setLibraryLoading] = useState(false);
  const [libraryError, setLibraryError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [busyFileIds, setBusyFileIds] = useState<number[]>([]);
  const [assistantMode, setAssistantMode] = useState<AssistantMode>("simple");
  const [settings, setSettings] = useState<Settings | null>(null);
  const [settingsDraft, setSettingsDraft] = useState<SettingsUpdate | null>(null);
  const [settingsLoading, setSettingsLoading] = useState(false);
  const [settingsSaving, setSettingsSaving] = useState(false);
  const [settingsError, setSettingsError] = useState<string | null>(null);
  const [settingsSuccess, setSettingsSuccess] = useState<string | null>(null);

  useEffect(() => {
    void bootstrap();
  }, []);

  async function bootstrap() {
    setBootstrapping(true);
    setAppError(null);
    try {
      const [chatList, archivedList, runtimeSettings] = await Promise.all([
        apiClient.listChats(),
        apiClient.listArchivedChats(),
        apiClient.getSettings(),
      ]);
      setChats(sortChats(chatList));
      setArchivedChats(sortChats(archivedList));
      setSettings(runtimeSettings);
      setSettingsDraft({
        chat_history_messages_count: runtimeSettings.chat_history_messages_count,
        max_similarities: runtimeSettings.max_similarities,
        min_similarities: runtimeSettings.min_similarities,
        similarity_score_threshold: runtimeSettings.similarity_score_threshold,
      });
      setAssistantMode(runtimeSettings.default_assistant_mode);

      if (chatList.length === 0) {
        const created = await apiClient.createChat();
        setChats([created]);
        setActiveChatInternal(created.id);
        setMessagesByChat({ [created.id]: [] });
      } else {
        const persistedChatId = window.localStorage.getItem(ACTIVE_CHAT_STORAGE_KEY);
        const nextChatId = chatList.some((chat) => chat.id === persistedChatId) ? persistedChatId : chatList[0].id;
        setActiveChatInternal(nextChatId);
      }
    } catch (error) {
      setAppError(error instanceof Error ? error.message : "Failed to load chats");
    } finally {
      setBootstrapping(false);
    }
  }

  function setActiveChatInternal(chatId: string | null) {
    setActiveChatId(chatId);
    if (chatId) {
      window.localStorage.setItem(ACTIVE_CHAT_STORAGE_KEY, chatId);
      return;
    }
    window.localStorage.removeItem(ACTIVE_CHAT_STORAGE_KEY);
  }

  async function ensureChatLoaded(chatId: string) {
    setActiveChatInternal(chatId);
    if (messagesByChat[chatId] !== undefined) {
      return;
    }

    setLoadingMessages(true);
    setAppError(null);
    try {
      const messages = await apiClient.getMessages(chatId);
      setMessagesByChat((current) => ({ ...current, [chatId]: messages }));
    } catch (error) {
      setAppError(error instanceof Error ? error.message : "Failed to load messages");
    } finally {
      setLoadingMessages(false);
    }
  }

  async function createChat() {
    setAppError(null);
    const chat = await apiClient.createChat();
    setChats((current) => sortChats([chat, ...current]));
    setMessagesByChat((current) => ({ ...current, [chat.id]: [] }));
    setActiveChatInternal(chat.id);
    return chat;
  }

  async function renameChat(chatId: string, chatName: string) {
    const updated = await apiClient.renameChat(chatId, { chat_name: chatName });
    setChats((current) => sortChats(current.map((chat) => (chat.id === chatId ? updated : chat))));
    setArchivedChats((current) => sortChats(current.map((chat) => (chat.id === chatId ? updated : chat))));
    return updated;
  }

  async function archiveChat(chatId: string) {
    const archived = await apiClient.archiveChat(chatId);
    setChats((current) => current.filter((chat) => chat.id !== chatId));
    setArchivedChats((current) => sortChats([archived, ...current.filter((chat) => chat.id !== chatId)]));

    const remaining = chats.filter((chat) => chat.id !== chatId);
    if (activeChatId === chatId) {
      if (remaining.length > 0) {
        setActiveChatInternal(remaining[0].id);
        return remaining[0].id;
      }
      const created = await apiClient.createChat();
      setChats([created]);
      setMessagesByChat((current) => ({ ...current, [created.id]: [] }));
      setActiveChatInternal(created.id);
      return created.id;
    }
    return activeChatId;
  }

  async function unarchiveChat(chatId: string) {
    const restored = await apiClient.unarchiveChat(chatId);
    setArchivedChats((current) => current.filter((chat) => chat.id !== chatId));
    setChats((current) => sortChats([restored, ...current.filter((chat) => chat.id !== chatId)]));
    return restored;
  }

  async function deleteChat(chatId: string) {
    await apiClient.deleteChat(chatId);
    setChats((current) => current.filter((chat) => chat.id !== chatId));
    setArchivedChats((current) => current.filter((chat) => chat.id !== chatId));
    setMessagesByChat((current) => {
      const next = { ...current };
      delete next[chatId];
      return next;
    });

    const remaining = chats.filter((chat) => chat.id !== chatId);
    if (activeChatId === chatId) {
      if (remaining.length > 0) {
        const nextActive = remaining[0].id;
        setActiveChatInternal(nextActive);
        return nextActive;
      }

      const created = await apiClient.createChat();
      setChats([created]);
      setMessagesByChat({ [created.id]: [] });
      setActiveChatInternal(created.id);
      return created.id;
    }

    return activeChatId ?? remaining[0]?.id ?? null;
  }

  async function downloadChat(chatId: string) {
    const payload = await apiClient.downloadChat(chatId);
    const safeName = payload.chat_name.replace(/[^a-z0-9-_]+/gi, "_").replace(/^_+|_+$/g, "") || "chat";
    triggerJsonDownload(`${safeName}-${payload.chat_id}.json`, payload);
  }

  async function sendMessage(content: string, attachments: File[] = [], mode: AssistantMode = assistantMode) {
    if (!activeChatId || !content.trim() || sending) {
      return;
    }

    const chatId = activeChatId;
    const optimisticAttachments = attachments.map<AttachmentMeta>((file) => ({
      file_name: file.name,
      file_type: file.name.split(".").pop()?.toLowerCase() ?? "unknown",
      extraction_method: null,
      quality: {},
    }));
    const optimisticUser = createOptimisticMessage(chatId, "user", content, "completed", optimisticAttachments);
    const optimisticAssistant = createOptimisticMessage(chatId, "assistant", mode === "refine" ? "Refining answer..." : "Thinking...", "pending");

    setSending(true);
    setAppError(null);
    setMessagesByChat((current) => ({
      ...current,
      [chatId]: [...(current[chatId] ?? []), optimisticUser, optimisticAssistant],
    }));

    try {
      const response = await apiClient.sendMessage(chatId, content, attachments, mode);
      setMessagesByChat((current) => ({
        ...current,
        [chatId]: [
          ...(current[chatId] ?? []).filter((message) => message.id !== optimisticUser.id && message.id !== optimisticAssistant.id),
          response.user_message,
          {
            ...response.assistant_message,
            sources: response.sources,
          },
        ],
      }));
      setChats((current) =>
        sortChats(current.map((chat) => (chat.id === chatId ? { ...chat, updated_at: new Date().toISOString() } : chat))),
      );
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Failed to send message";
      setMessagesByChat((current) => ({
        ...current,
        [chatId]: [
          ...(current[chatId] ?? []).filter((message) => message.id !== optimisticAssistant.id),
          {
            ...optimisticAssistant,
            content: errorMessage,
            status: "error",
            error: errorMessage,
          },
        ],
      }));
      setAppError(errorMessage);
    } finally {
      setSending(false);
    }
  }

  async function loadSettings() {
    setSettingsLoading(true);
    setSettingsError(null);
    try {
      const runtimeSettings = await apiClient.getSettings();
      setSettings(runtimeSettings);
      setSettingsDraft({
        chat_history_messages_count: runtimeSettings.chat_history_messages_count,
        max_similarities: runtimeSettings.max_similarities,
        min_similarities: runtimeSettings.min_similarities,
        similarity_score_threshold: runtimeSettings.similarity_score_threshold,
      });
      setAssistantMode((current) => (runtimeSettings.available_assistant_modes.includes(current) ? current : runtimeSettings.default_assistant_mode));
    } catch (error) {
      setSettingsError(error instanceof Error ? error.message : "Failed to load settings");
    } finally {
      setSettingsLoading(false);
    }
  }

  function updateSettingsDraft(patch: Partial<SettingsUpdate>) {
    setSettingsDraft((current) => (current ? { ...current, ...patch } : current));
    setSettingsSuccess(null);
  }

  async function saveSettings() {
    if (!settingsDraft) {
      return null;
    }

    setSettingsSaving(true);
    setSettingsError(null);
    setSettingsSuccess(null);
    try {
      const updated = await apiClient.updateSettings(settingsDraft);
      setSettings(updated);
      setSettingsDraft({
        chat_history_messages_count: updated.chat_history_messages_count,
        max_similarities: updated.max_similarities,
        min_similarities: updated.min_similarities,
        similarity_score_threshold: updated.similarity_score_threshold,
      });
      setSettingsSuccess("Settings saved and applied live.");
      return updated;
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to save settings";
      setSettingsError(message);
      return null;
    } finally {
      setSettingsSaving(false);
    }
  }

  async function loadLibrary() {
    setLibraryLoading(true);
    setLibraryError(null);
    try {
      setLibrary(await apiClient.listLibraryFiles());
    } catch (error) {
      setLibraryError(error instanceof Error ? error.message : "Failed to load library");
    } finally {
      setLibraryLoading(false);
    }
  }

  async function toggleLibraryFile(file: LibraryFile) {
    setBusyFileIds((current) => [...current, file.id]);
    setLibraryError(null);
    try {
      const updated = await apiClient.updateLibraryFile(file.id, { is_enabled: !file.is_enabled });
      setLibrary((current) =>
        current
          ? { ...current, files: current.files.map((item) => (item.id === file.id ? updated : item)) }
          : current,
      );
    } catch (error) {
      setLibraryError(error instanceof Error ? error.message : "Failed to update file");
    } finally {
      setBusyFileIds((current) => current.filter((id) => id !== file.id));
    }
  }

  async function deleteLibraryFile(fileId: number) {
    setBusyFileIds((current) => [...current, fileId]);
    setLibraryError(null);
    try {
      await apiClient.deleteLibraryFile(fileId);
      await loadLibrary();
    } catch (error) {
      setLibraryError(error instanceof Error ? error.message : "Failed to delete file");
    } finally {
      setBusyFileIds((current) => current.filter((id) => id !== fileId));
    }
  }

  async function uploadLibraryFiles(files: File[], tagsByFile: Record<string, string[]>) {
    setUploading(true);
    setLibraryError(null);
    try {
      await apiClient.uploadLibraryFiles(files, tagsByFile);
      await loadLibrary();
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to upload files";
      setLibraryError(message);
      throw error;
    } finally {
      setUploading(false);
    }
  }

  const activeMessages = useMemo(() => {
    if (!activeChatId) {
      return [];
    }
    return messagesByChat[activeChatId] ?? [];
  }, [activeChatId, messagesByChat]);

  return {
    bootstrapping,
    chats,
    archivedChats,
    activeChatId,
    activeMessages,
    loadingMessages,
    sending,
    appError,
    library,
    libraryLoading,
    libraryError,
    uploading,
    busyFileIds,
    assistantMode,
    settings,
    settingsDraft,
    settingsLoading,
    settingsSaving,
    settingsError,
    settingsSuccess,
    attachmentRules: {
      maxFiles: ATTACHMENT_MAX_FILES,
      allowedExtensions: ATTACHMENT_ALLOWED_EXTENSIONS,
    },
    bootstrap,
    ensureChatLoaded,
    createChat,
    renameChat,
    archiveChat,
    unarchiveChat,
    deleteChat,
    downloadChat,
    sendMessage,
    setAssistantMode,
    loadSettings,
    updateSettingsDraft,
    saveSettings,
    loadLibrary,
    toggleLibraryFile,
    deleteLibraryFile,
    uploadLibraryFiles,
  };
}
