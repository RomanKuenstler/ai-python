import { ChatInput } from "../input/ChatInput";
import { MessageList } from "../messages/MessageList";
import type { Message } from "../../types/chat";

type ChatViewProps = {
  messages: Message[];
  sending: boolean;
  loadingMessages: boolean;
  error: string | null;
  attachmentRules: {
    maxFiles: number;
    allowedExtensions: string[];
  };
  onSend: (value: string, attachments: File[]) => Promise<void>;
};

export function ChatView({ messages, sending, loadingMessages, error, attachmentRules, onSend }: ChatViewProps) {
  return (
    <section className="chat-column">
      <div className="page-heading">
        <div>
          <p className="section-label">Grounded answers</p>
          <h2 className="page-title">Conversation</h2>
        </div>
        {error ? <p className="chat-error">{error}</p> : null}
      </div>
      <div className="chat-thread-card">
        <MessageList messages={messages} loadingMessages={loadingMessages} />
      </div>
      <div className="composer-dock">
        <ChatInput disabled={sending} attachmentRules={attachmentRules} onSend={onSend} />
      </div>
    </section>
  );
}
