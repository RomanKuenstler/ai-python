import { useEffect, useMemo, useState } from "react";
import { apiClient } from "../api/client";
import type { Chat, Message } from "../types/chat";

const ACTIVE_CHAT_STORAGE_KEY = "local-rag-active-chat";

function createOptimisticMessage(chatId: string, role: "user" | "assistant", content: string, status: Message["status"]): Message {
  return {
    id: `temp-${role}-${crypto.randomUUID()}`,
    chat_id: chatId,
    role,
    content,
    status,
    created_at: new Date().toISOString(),
    sources: [],
  };
}

export function useChatApp() {
  const [chats, setChats] = useState<Chat[]>([]);
  const [activeChatId, setActiveChatId] = useState<string | null>(null);
  const [messagesByChat, setMessagesByChat] = useState<Record<string, Message[]>>({});
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [sending, setSending] = useState(false);
  const [appError, setAppError] = useState<string | null>(null);

  useEffect(() => {
    void bootstrap();
  }, []);

  async function bootstrap() {
    setAppError(null);
    try {
      const chatList = await apiClient.listChats();
      if (chatList.length === 0) {
        const chat = await apiClient.createChat();
        setChats([chat]);
        setActiveChat(chat.id);
        await loadMessages(chat.id);
        return;
      }

      setChats(chatList);
      const persistedChatId = window.localStorage.getItem(ACTIVE_CHAT_STORAGE_KEY);
      const nextChatId = chatList.some((chat) => chat.id === persistedChatId) ? persistedChatId : chatList[0].id;
      if (nextChatId) {
        setActiveChat(nextChatId);
        await loadMessages(nextChatId);
      }
    } catch (error) {
      setAppError(error instanceof Error ? error.message : "Failed to load chats");
    }
  }

  function setActiveChat(chatId: string) {
    setActiveChatId(chatId);
    window.localStorage.setItem(ACTIVE_CHAT_STORAGE_KEY, chatId);
  }

  async function loadMessages(chatId: string) {
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
    try {
      const chat = await apiClient.createChat();
      setChats((current) => [chat, ...current]);
      setMessagesByChat((current) => ({ ...current, [chat.id]: [] }));
      setActiveChat(chat.id);
    } catch (error) {
      setAppError(error instanceof Error ? error.message : "Failed to create chat");
    }
  }

  async function selectChat(chatId: string) {
    setActiveChat(chatId);
    if (messagesByChat[chatId] === undefined) {
      await loadMessages(chatId);
    }
  }

  async function sendMessage(content: string) {
    if (!activeChatId || !content.trim() || sending) {
      return;
    }

    const chatId = activeChatId;
    const optimisticUser = createOptimisticMessage(chatId, "user", content, "completed");
    const optimisticAssistant = createOptimisticMessage(chatId, "assistant", "Thinking...", "pending");

    setSending(true);
    setAppError(null);
    setMessagesByChat((current) => ({
      ...current,
      [chatId]: [...(current[chatId] ?? []), optimisticUser, optimisticAssistant],
    }));

    try {
      const response = await apiClient.sendMessage(chatId, content);
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
          .map((chat) =>
            chat.id === chatId ? { ...chat, updated_at: new Date().toISOString() } : chat,
          )
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

  const activeMessages = useMemo(() => {
    if (!activeChatId) {
      return [];
    }
    return messagesByChat[activeChatId] ?? [];
  }, [activeChatId, messagesByChat]);

  return {
    chats,
    activeChatId,
    activeMessages,
    loadingMessages,
    sending,
    appError,
    createChat,
    selectChat,
    sendMessage,
  };
}
