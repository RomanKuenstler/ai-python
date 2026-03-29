import type { Chat } from "../../types/chat";

type SidebarProps = {
  chats: Chat[];
  activeChatId: string | null;
  onCreateChat: () => void;
  onSelectChat: (chatId: string) => void;
};

export function Sidebar({ chats, activeChatId, onCreateChat, onSelectChat }: SidebarProps) {
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <div>
          <p className="eyebrow">Local Knowledge</p>
          <h1>Local RAG</h1>
        </div>
        <button className="new-chat-button" type="button" onClick={onCreateChat}>
          New chat
        </button>
      </div>

      <div className="chat-list" aria-label="Chats">
        {chats.map((chat) => (
          <button
            key={chat.id}
            className={`chat-list-item${chat.id === activeChatId ? " active" : ""}`}
            type="button"
            onClick={() => onSelectChat(chat.id)}
          >
            <span>{chat.chat_name}</span>
          </button>
        ))}
      </div>

      <div className="sidebar-footer">
        <span>Future user menu</span>
      </div>
    </div>
  );
}
