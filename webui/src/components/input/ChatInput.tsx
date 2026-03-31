import { useEffect, useMemo, useRef, useState } from "react";
import { Icon } from "../common/Icons";
import type { AssistantMode } from "../../types/chat";

type ChatInputProps = {
  disabled: boolean;
  attachmentRules: {
    maxFiles: number;
    allowedExtensions: string[];
  };
  onSend: (value: string, attachments: File[], mode: AssistantMode) => Promise<void>;
  assistantMode: AssistantMode;
};

export function ChatInput({ disabled, assistantMode, attachmentRules, onSend }: ChatInputProps) {
  const [value, setValue] = useState("");
  const [attachments, setAttachments] = useState<File[]>([]);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const acceptValue = useMemo(() => attachmentRules.allowedExtensions.join(","), [attachmentRules.allowedExtensions]);

  useEffect(() => {
    if (!textareaRef.current) {
      return;
    }
    textareaRef.current.style.height = "0px";
    textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 192)}px`;
  }, [value]);

  function validateFiles(nextFiles: File[]) {
    if (nextFiles.length > attachmentRules.maxFiles) {
      return `You can attach up to ${attachmentRules.maxFiles} files.`;
    }
    for (const file of nextFiles) {
      const extension = `.${file.name.split(".").pop()?.toLowerCase() ?? ""}`;
      if (!attachmentRules.allowedExtensions.includes(extension)) {
        return `Unsupported attachment type: ${file.name}`;
      }
    }
    return null;
  }

  function handleAttachmentSelection(fileList: FileList | null) {
    const incoming = Array.from(fileList ?? []);
    if (incoming.length === 0) {
      return;
    }
    const merged = [...attachments];
    for (const file of incoming) {
      if (!merged.some((item) => item.name === file.name && item.size === file.size)) {
        merged.push(file);
      }
    }
    const nextError = validateFiles(merged);
    if (nextError) {
      setError(nextError);
      return;
    }
    setAttachments(merged);
    setError(null);
  }

  async function handleSubmit() {
    if (!value.trim() || disabled) {
      return;
    }

    const nextValue = value;
    const nextAttachments = attachments;
    setValue("");
    setAttachments([]);
    setError(null);
    await onSend(nextValue, nextAttachments, assistantMode);
  }

  return (
    <form
      className="composer"
      onSubmit={(event) => {
        event.preventDefault();
        void handleSubmit();
      }}
    >
      <div className="composer-input-shell">
        <input
          ref={inputRef}
          type="file"
          className="composer-file-input"
          hidden
          multiple
          accept={acceptValue}
          onChange={(event) => handleAttachmentSelection(event.target.files)}
        />
      {attachments.length > 0 ? (
        <div className="attachment-preview-list composer-attachment-list composer-attachment-chip-list">
          {attachments.map((file) => (
            <div key={`${file.name}-${file.size}`} className="attachment-chip composer-attachment-chip">
              <div className={`composer-attachment-icon ${file.name.endsWith(".pdf") ? "is-red" : file.name.endsWith(".html") || file.name.endsWith(".htm") ? "is-blue" : file.name.endsWith(".epub") ? "is-purple" : file.name.endsWith(".md") || file.name.endsWith(".txt") ? "is-gray" : "is-green"}`}>
                <span className="composer-attachment-icon-label">{file.name.split(".").pop()?.slice(0, 3).toUpperCase() ?? "FILE"}</span>
              </div>
              <div className="composer-attachment-meta">
                <span className="composer-attachment-name">{file.name}</span>
                <span className="composer-attachment-ext">{file.name.split(".").pop()?.toUpperCase() ?? "FILE"}</span>
              </div>
              <button
                type="button"
                className="attachment-remove-button composer-attachment-remove"
                onClick={() => setAttachments((current) => current.filter((item) => !(item.name === file.name && item.size === file.size)))}
                disabled={disabled}
                aria-label={`Remove ${file.name}`}
              >
                x
              </button>
            </div>
          ))}
        </div>
      ) : null}
        <div className="composer-entry-row">
          <button className="attachment-button composer-attach-button" type="button" onClick={() => inputRef.current?.click()} disabled={disabled} aria-label="Attach files">
            +
          </button>
          <textarea
            ref={textareaRef}
            className="composer-input"
            rows={1}
            placeholder="Ask anything about your knowledge base..."
            value={value}
            disabled={disabled}
            onChange={(event) => setValue(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                void handleSubmit();
              }
            }}
          />
        </div>
      </div>
      <button className="send-button send" type="submit" disabled={disabled || !value.trim()} aria-label="Send prompt">
        <Icon name="arrow-up" className="send-icon" />
      </button>
      {error ? <p className="inline-error composer-attachment-notice invalid">{error}</p> : null}
    </form>
  );
}
