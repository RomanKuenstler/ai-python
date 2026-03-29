import { useEffect, useRef } from "react";
import type { Message } from "../../types/chat";
import { MessageBubble } from "./MessageBubble";

type MessageListProps = {
  messages: Message[];
  loadingMessages: boolean;
};

export function MessageList({ messages, loadingMessages }: MessageListProps) {
  const endRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages]);

  if (loadingMessages) {
    return <div className="empty-state">Loading chat history...</div>;
  }

  if (messages.length === 0) {
    return <div className="empty-state">Ask a question to start a grounded conversation with your local knowledge base.</div>;
  }

  return (
    <div className="message-list">
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
      <div ref={endRef} />
    </div>
  );
}
