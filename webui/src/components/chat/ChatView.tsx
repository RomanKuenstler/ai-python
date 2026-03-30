import { ChatInput } from "../input/ChatInput";
import { MessageList } from "../messages/MessageList";
import type { AssistantMode, Message } from "../../types/chat";

type ChatViewProps = {
  messages: Message[];
  sending: boolean;
  loadingMessages: boolean;
  error: string | null;
  assistantMode: AssistantMode;
  availableModes: AssistantMode[];
  attachmentRules: {
    maxFiles: number;
    allowedExtensions: string[];
  };
  onAssistantModeChange: (mode: AssistantMode) => void;
  onSend: (value: string, attachments: File[], mode: AssistantMode) => Promise<void>;
};

export function ChatView({
  messages,
  sending,
  loadingMessages,
  error,
  assistantMode,
  availableModes,
  attachmentRules,
  onAssistantModeChange,
  onSend,
}: ChatViewProps) {
  return (
    <section className="chat-column">
      <div className="page-heading">
        <div>
          <p className="section-label">Grounded answers</p>
          <h2 className="page-title">Chat</h2>
        </div>
        {error ? <p className="chat-error">{error}</p> : null}
      </div>
      <div className="chat-thread-card chat">
        <MessageList messages={messages} loadingMessages={loadingMessages} />
      </div>
      <div className="composer-dock">
        <ChatInput
          disabled={sending}
          assistantMode={assistantMode}
          availableModes={availableModes}
          attachmentRules={attachmentRules}
          onAssistantModeChange={onAssistantModeChange}
          onSend={onSend}
        />
      </div>
    </section>
  );
}
