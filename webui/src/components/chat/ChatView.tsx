import { ChatInput } from "../input/ChatInput";
import { MessageList } from "../messages/MessageList";
import type { Message } from "../../types/chat";

type ChatViewProps = {
  messages: Message[];
  sending: boolean;
  loadingMessages: boolean;
  error: string | null;
  onSend: (value: string) => Promise<void>;
};

export function ChatView({ messages, sending, loadingMessages, error, onSend }: ChatViewProps) {
  return (
    <section className="chat-view">
      <div className="chat-header">
        <div>
          <p className="eyebrow">Grounded answers</p>
          <h2>Conversation</h2>
        </div>
        {error ? <p className="chat-error">{error}</p> : null}
      </div>
      <div className="chat-scroll-area">
        <MessageList messages={messages} loadingMessages={loadingMessages} />
      </div>
      <div className="chat-input-area">
        <ChatInput disabled={sending} onSend={onSend} />
      </div>
    </section>
  );
}
