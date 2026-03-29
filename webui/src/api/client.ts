import type { Chat, Message, MessageResponse } from "../types/chat";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
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
  getMessages(chatId: string) {
    return request<Message[]>(`/api/chats/${chatId}/messages`);
  },
  sendMessage(chatId: string, content: string) {
    return request<MessageResponse>(`/api/chats/${chatId}/messages`, {
      method: "POST",
      body: JSON.stringify({ content }),
    });
  },
};
