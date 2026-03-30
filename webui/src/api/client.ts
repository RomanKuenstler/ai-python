import type {
  AssistantMode,
  Chat,
  ChatDownload,
  ChatUpdate,
  LibraryFile,
  LibraryResponse,
  LibraryUploadResponse,
  Message,
  MessageResponse,
  Settings,
  SettingsUpdate,
} from "../types/chat";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers ?? {});
  const isFormData = init?.body instanceof FormData;
  if (!isFormData && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
  });

  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(body?.detail ?? `Request failed with status ${response.status}`);
  }

  return (await response.json()) as T;
}

export const apiClient = {
  createChat() {
    return request<Chat>("/api/chats", { method: "POST" });
  },
  listChats() {
    return request<Chat[]>("/api/chats");
  },
  listArchivedChats() {
    return request<Chat[]>("/api/chats/archived");
  },
  renameChat(chatId: string, payload: ChatUpdate) {
    return request<Chat>(`/api/chats/${chatId}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  },
  archiveChat(chatId: string) {
    return request<Chat>(`/api/chats/${chatId}/archive`, { method: "PATCH" });
  },
  unarchiveChat(chatId: string) {
    return request<Chat>(`/api/chats/${chatId}/unarchive`, { method: "PATCH" });
  },
  deleteChat(chatId: string) {
    return request<Chat>(`/api/chats/${chatId}`, { method: "DELETE" });
  },
  downloadChat(chatId: string) {
    return request<ChatDownload>(`/api/chats/${chatId}/download`);
  },
  getMessages(chatId: string) {
    return request<Message[]>(`/api/chats/${chatId}/messages`);
  },
  sendMessage(chatId: string, message: string, attachments: File[], assistantMode: AssistantMode) {
    if (attachments.length === 0) {
      return request<MessageResponse>(`/api/chats/${chatId}/messages`, {
        method: "POST",
        body: JSON.stringify({ message, assistant_mode: assistantMode }),
      });
    }

    const formData = new FormData();
    formData.append("message", message);
    formData.append("assistant_mode", assistantMode);
    attachments.forEach((file) => formData.append("files", file));
    return request<MessageResponse>(`/api/chats/${chatId}/messages`, {
      method: "POST",
      body: formData,
    });
  },
  getSettings() {
    return request<Settings>("/api/settings");
  },
  updateSettings(payload: SettingsUpdate) {
    return request<Settings>("/api/settings", {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  },
  listLibraryFiles() {
    return request<LibraryResponse>("/api/library/files");
  },
  updateLibraryFile(fileId: number, payload: { is_enabled: boolean }) {
    return request<LibraryFile>(`/api/library/files/${fileId}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  },
  deleteLibraryFile(fileId: number) {
    return request<LibraryFile>(`/api/library/files/${fileId}`, { method: "DELETE" });
  },
  uploadLibraryFiles(files: File[], tagsByFile: Record<string, string[]>) {
    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));
    formData.append("tags_by_file", JSON.stringify(tagsByFile));
    return request<LibraryUploadResponse>("/api/library/files/upload", {
      method: "POST",
      body: formData,
    });
  },
};
