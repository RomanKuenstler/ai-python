import { useState } from "react";

type ChatInputProps = {
  disabled: boolean;
  onSend: (value: string) => Promise<void>;
};

export function ChatInput({ disabled, onSend }: ChatInputProps) {
  const [value, setValue] = useState("");

  async function handleSubmit() {
    if (!value.trim() || disabled) {
      return;
    }

    const nextValue = value;
    setValue("");
    await onSend(nextValue);
  }

  return (
    <div className="chat-input-shell">
      <textarea
        className="chat-input"
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
      <button className="send-button" type="button" disabled={disabled || !value.trim()} onClick={() => void handleSubmit()}>
        <span className="sr-only">Send message</span>
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M3 20.5v-17l18 8.5-18 8.5Zm2-3.1 10.9-5.4L5 6.6v3.8l5.6 1.6-5.6 1.6v3.8Z" />
        </svg>
      </button>
    </div>
  );
}
