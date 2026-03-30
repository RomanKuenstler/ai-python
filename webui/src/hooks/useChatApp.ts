import { useEffect, useMemo, useState } from "react";
import { apiClient } from "../api/client";
import type { AttachmentMeta, Chat, LibraryFile, LibraryResponse, Message } from "../types/chat";

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

export function useChatApp() {
  const [bootstrapping, setBootstrapping] = useState(true);
  const [chats, setChats] = useState<Chat[]>([]);
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

  useEffect(() => {
    void bootstrap();
  }, []);

  async function bootstrap() {
    setBootstrapping(true);
    setAppError(null);
    try {
      const chatList = await apiClient.listChats();
      if (chatList.length === 0) {
        const created = await apiClient.createChat();
        setChats([created]);
        setActiveChatInternal(created.id);
        setMessagesByChat({ [created.id]: [] });
      } else {
        setChats(chatList);
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
    }
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
    setChats((current) => [chat, ...current]);
    setMessagesByChat((current) => ({ ...current, [chat.id]: [] }));
    setActiveChatInternal(chat.id);
    return chat;
  }

  async function renameChat(chatId: string, chatName: string) {
    const updated = await apiClient.renameChat(chatId, { chat_name: chatName });
    setChats((current) =>
      current
        .map((chat) => (chat.id === chatId ? updated : chat))
        .sort((left, right) => right.updated_at.localeCompare(left.updated_at)),
    );
    return updated;
  }

  async function deleteChat(chatId: string) {
    await apiClient.deleteChat(chatId);
    setChats((current) => current.filter((chat) => chat.id !== chatId));
    setMessagesByChat((current) => {
      const next = { ...current };
      delete next[chatId];
      return next;
    });

    const remaining = chats.filter((chat) => chat.id !== chatId);
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

  async function sendMessage(content: string, attachments: File[] = []) {
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
    const optimisticAssistant = createOptimisticMessage(chatId, "assistant", "Thinking...", "pending");

    setSending(true);
    setAppError(null);
    setMessagesByChat((current) => ({
      ...current,
      [chatId]: [...(current[chatId] ?? []), optimisticUser, optimisticAssistant],
    }));

    try {
      const response = await apiClient.sendMessage(chatId, content, attachments);
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
        current
          .map((chat) => (chat.id === chatId ? { ...chat, updated_at: new Date().toISOString() } : chat))
          .sort((left, right) => right.updated_at.localeCompare(left.updated_at)),
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
    attachmentRules: {
      maxFiles: ATTACHMENT_MAX_FILES,
      allowedExtensions: ATTACHMENT_ALLOWED_EXTENSIONS,
    },
    bootstrap,
    ensureChatLoaded,
    createChat,
    renameChat,
    deleteChat,
    sendMessage,
    loadLibrary,
    toggleLibraryFile,
    deleteLibraryFile,
    uploadLibraryFiles,
  };
}
