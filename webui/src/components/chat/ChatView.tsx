import { ChatInput } from "../input/ChatInput";
import { MessageList } from "../messages/MessageList";
import type { AssistantMode, Message } from "../../types/chat";

type ChatViewProps = {
  messages: Message[];
  sending: boolean;
  loadingMessages: boolean;
  error: string | null;
  assistantMode: AssistantMode;
  attachmentRules: {
    maxFiles: number;
    allowedExtensions: string[];
  };
  onSend: (value: string, attachments: File[], mode: AssistantMode) => Promise<void>;
};

export function ChatView({
  messages,
  sending,
  loadingMessages,
  error,
  assistantMode,
  attachmentRules,
  onSend,
}: ChatViewProps) {
  return (
    <section className="chat-column">
      {error ? <p className="chat-error chat-error-banner">{error}</p> : null}
      <div className="chat-thread-card chat" aria-label="Conversation">
        <MessageList messages={messages} loadingMessages={loadingMessages} />
      </div>
      <ChatInput
        disabled={sending}
        assistantMode={assistantMode}
        attachmentRules={attachmentRules}
        onSend={onSend}
      />
    </section>
  );
}
