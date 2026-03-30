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

  return (
    <article className={`message-bubble ${message.role}`}>
      <div className="message-meta">
        <span>{message.role === "user" ? "You" : "Assistant"}</span>
        {message.status === "pending" ? <span className="message-status">Working...</span> : null}
        {message.status === "error" ? <span className="message-status error">Error</span> : null}
      </div>
      <div className="message-content">
        {message.role === "assistant" ? (
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
            <span key={`${message.id}-${attachment.file_name}`} className="message-attachment-pill">
              {attachment.file_name}
            </span>
          ))}
        </div>
      ) : null}
      {message.role === "assistant" && message.sources.length > 0 ? (
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
