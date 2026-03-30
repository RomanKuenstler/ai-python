import { useMemo, useRef, useState } from "react";

type ChatInputProps = {
  disabled: boolean;
  attachmentRules: {
    maxFiles: number;
    allowedExtensions: string[];
  };
  onSend: (value: string, attachments: File[]) => Promise<void>;
};

export function ChatInput({ disabled, attachmentRules, onSend }: ChatInputProps) {
  const [value, setValue] = useState("");
  const [attachments, setAttachments] = useState<File[]>([]);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const acceptValue = useMemo(() => attachmentRules.allowedExtensions.join(","), [attachmentRules.allowedExtensions]);

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
    await onSend(nextValue, nextAttachments);
  }

  return (
    <div className="composer-shell">
      {attachments.length > 0 ? (
        <div className="attachment-preview-list">
          {attachments.map((file) => (
            <div key={`${file.name}-${file.size}`} className="attachment-chip">
              <span>{file.name}</span>
              <button
                type="button"
                className="attachment-remove-button"
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
      <textarea
        className="composer-input"
        rows={1}
        placeholder="Ask something about your indexed documents..."
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
      <div className="composer-actions">
        <input
          ref={inputRef}
          type="file"
          hidden
          multiple
          accept={acceptValue}
          onChange={(event) => handleAttachmentSelection(event.target.files)}
        />
        <button className="attachment-button" type="button" onClick={() => inputRef.current?.click()} disabled={disabled}>
          Attach
        </button>
        <button className="send-button" type="button" disabled={disabled || !value.trim()} onClick={() => void handleSubmit()}>
          Send
        </button>
      </div>
      {error ? <p className="inline-error">{error}</p> : null}
    </div>
  );
}
