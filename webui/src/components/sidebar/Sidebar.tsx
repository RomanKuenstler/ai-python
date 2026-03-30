import { useEffect, useRef, useState } from "react";
import type { Chat } from "../../types/chat";
import { Dialog } from "../common/Dialog";

type SidebarProps = {
  chats: Chat[];
  activeChatId: string | null;
  activeView: "chat" | "library";
  onCreateChat: () => void;
  onOpenLibrary: () => void;
  onSelectChat: (chatId: string) => void;
  onRenameChat: (chatId: string, chatName: string) => void;
  onDeleteChat: (chatId: string) => void;
};

export function Sidebar({
  chats,
  activeChatId,
  activeView,
  onCreateChat,
  onOpenLibrary,
  onSelectChat,
  onRenameChat,
  onDeleteChat,
}: SidebarProps) {
  const [menuChatId, setMenuChatId] = useState<string | null>(null);
  const [renameTarget, setRenameTarget] = useState<Chat | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Chat | null>(null);
  const [renameValue, setRenameValue] = useState("");
  const menuRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    function handleDocumentClick(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setMenuChatId(null);
      }
    }

    function handleEscape(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setMenuChatId(null);
      }
    }

    document.addEventListener("mousedown", handleDocumentClick);
    document.addEventListener("keydown", handleEscape);
    return () => {
      document.removeEventListener("mousedown", handleDocumentClick);
      document.removeEventListener("keydown", handleEscape);
    };
  }, []);

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <div>
          <p className="eyebrow">Local Knowledge</p>
          <h1>Local RAG</h1>
        </div>
      </div>

      <div className="sidebar-primary-actions">
        <button className="new-chat-button" type="button" onClick={onCreateChat}>
          New chat
        </button>
        <button className={`library-button${activeView === "library" ? " active" : ""}`} type="button" onClick={onOpenLibrary}>
          Library
        </button>
      </div>

      <div className="chat-list" aria-label="Chats">
        {chats.map((chat) => (
          <div key={chat.id} className={`chat-list-row${chat.id === activeChatId && activeView === "chat" ? " active" : ""}`}>
            <button className="chat-list-item" type="button" onClick={() => onSelectChat(chat.id)}>
              <span>{chat.chat_name}</span>
            </button>
            <div className="chat-menu-anchor" ref={menuChatId === chat.id ? menuRef : null}>
              <button
                className="chat-menu-button"
                type="button"
                aria-label={`Chat options for ${chat.chat_name}`}
                onClick={(event) => {
                  event.stopPropagation();
                  setMenuChatId((current) => (current === chat.id ? null : chat.id));
                }}
              >
                ...
              </button>
              {menuChatId === chat.id ? (
                <div className="chat-item-menu">
                  <button
                    type="button"
                    onClick={() => {
                      setRenameTarget(chat);
                      setRenameValue(chat.chat_name);
                      setMenuChatId(null);
                    }}
                  >
                    Rename
                  </button>
                  <button
                    type="button"
                    className="danger-text"
                    onClick={() => {
                      setDeleteTarget(chat);
                      setMenuChatId(null);
                    }}
                  >
                    Delete
                  </button>
                </div>
              ) : null}
            </div>
          </div>
        ))}
      </div>

      <div className="sidebar-footer">
        <span>Future user menu</span>
      </div>

      {renameTarget ? (
        <Dialog
          title="Rename Chat"
          onClose={() => setRenameTarget(null)}
          actions={
            <>
              <button className="secondary-button" type="button" onClick={() => setRenameTarget(null)}>
                Cancel
              </button>
              <button
                className="primary-button"
                type="button"
                disabled={renameValue.trim().length === 0}
                onClick={() => {
                  onRenameChat(renameTarget.id, renameValue.trim());
                  setRenameTarget(null);
                }}
              >
                Save
              </button>
            </>
          }
        >
          <input className="dialog-input" type="text" value={renameValue} onChange={(event) => setRenameValue(event.target.value)} />
        </Dialog>
      ) : null}

      {deleteTarget ? (
        <Dialog
          title="Delete Chat"
          onClose={() => setDeleteTarget(null)}
          actions={
            <>
              <button className="secondary-button" type="button" onClick={() => setDeleteTarget(null)}>
                Keep
              </button>
              <button
                className="danger-button"
                type="button"
                onClick={() => {
                  onDeleteChat(deleteTarget.id);
                  setDeleteTarget(null);
                }}
              >
                Delete
              </button>
            </>
          }
        >
          <p>
            Delete <strong>{deleteTarget.chat_name}</strong> and all of its messages?
          </p>
        </Dialog>
      ) : null}
    </div>
  );
}
