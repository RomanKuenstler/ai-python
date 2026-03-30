import { useState } from "react";
import ReactMarkdown from "react-markdown";
import rehypeSanitize from "rehype-sanitize";
import remarkGfm from "remark-gfm";
import type { Message } from "../../types/chat";
import { SourcesPanel } from "../sources/SourcesPanel";

type MessageBubbleProps = {
  message: Message;
};

export function MessageBubble({ message }: MessageBubbleProps) {
  const [sourcesOpen, setSourcesOpen] = useState(false);
  const isAssistant = message.role === "assistant";

  return (
    <article className={`message-bubble ${message.role}`}>
      <div className="message-meta">
        <span>{isAssistant ? "Assistant" : "You"}</span>
        {message.status === "pending" ? <span className="message-status">Working...</span> : null}
        {message.status === "error" ? <span className="message-status error">Error</span> : null}
      </div>
      <div className="message-content">
        {isAssistant ? (
          <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeSanitize]}>
            {message.content}
          </ReactMarkdown>
        ) : (
          message.content
        )}
      </div>
      {message.attachments.length > 0 ? (
        <div className="message-attachments">
          {message.attachments.map((attachment) => (
            <span key={`${message.id}-${attachment.file_name}`} className="message-attachment-pill composer-attachment-chip">
              {attachment.file_name}
            </span>
          ))}
        </div>
      ) : null}
      {isAssistant && message.sources.length > 0 ? (
        <div className="sources-wrap">
          <button className="sources-button" type="button" onClick={() => setSourcesOpen((current) => !current)}>
            Sources
          </button>
          <SourcesPanel open={sourcesOpen} onClose={() => setSourcesOpen(false)} sources={message.sources} />
        </div>
      ) : null}
    </article>
  );
}
