import { useEffect, useRef, useState } from "react";
import type { Chat } from "../../types/chat";
import { Dialog } from "../common/Dialog";

type SidebarProps = {
  chats: Chat[];
  activeChatId: string | null;
  activeView: "chat" | "library";
  onCreateChat: () => void;
  onOpenLibrary: () => void;
  onOpenArchive: () => void;
  onOpenInfo: () => void;
  onOpenHelp: () => void;
  onOpenPreferences: (tab?: "general" | "personalization" | "settings" | "archive") => void;
  onSelectChat: (chatId: string) => void;
  onRenameChat: (chatId: string, chatName: string) => void;
  onArchiveChat: (chatId: string) => void;
  onDownloadChat: (chatId: string) => void;
  onDeleteChat: (chatId: string) => void;
};

export function Sidebar({
  chats,
  activeChatId,
  activeView,
  onCreateChat,
  onOpenLibrary,
  onOpenArchive,
  onOpenInfo,
  onOpenHelp,
  onOpenPreferences,
  onSelectChat,
  onRenameChat,
  onArchiveChat,
  onDownloadChat,
  onDeleteChat,
}: SidebarProps) {
  const [menuChatId, setMenuChatId] = useState<string | null>(null);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [renameTarget, setRenameTarget] = useState<Chat | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Chat | null>(null);
  const [renameValue, setRenameValue] = useState("");
  const menuRef = useRef<HTMLDivElement | null>(null);
  const userMenuRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    function handleDocumentClick(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setMenuChatId(null);
      }
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setUserMenuOpen(false);
      }
    }

    function handleEscape(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setMenuChatId(null);
        setUserMenuOpen(false);
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
    <div className="side-nav-inner">
      <div className="side-nav-top">
        <button className="side-nav-item" type="button" onClick={onCreateChat}>
          New chat
        </button>
        <button className={`side-nav-item${activeView === "library" ? " active" : ""}`} type="button" onClick={onOpenLibrary}>
          Library
        </button>
        <button className="side-nav-item" type="button" onClick={onOpenArchive}>
          Archive chats
        </button>
      </div>

      <p className="side-nav-headline">Chats</p>

      <div className="side-nav-chat-list" aria-label="Chats">
        {chats.map((chat) => (
          <div
            key={chat.id}
            className={`side-nav-chat-row${chat.id === activeChatId && activeView === "chat" ? " active" : ""}${
              menuChatId === chat.id ? " menu-open" : ""
            }`}
          >
            <button className={`side-nav-chat-item${chat.id === activeChatId && activeView === "chat" ? " active" : ""}`} type="button" onClick={() => onSelectChat(chat.id)}>
              <span>{chat.chat_name}</span>
            </button>
            <div className="chat-item-actions" ref={menuChatId === chat.id ? menuRef : null}>
              <button
                className="chat-item-actions-trigger"
                type="button"
                aria-label={`Chat options for ${chat.chat_name}`}
                aria-expanded={menuChatId === chat.id}
                onClick={(event) => {
                  event.stopPropagation();
                  setMenuChatId((current) => (current === chat.id ? null : chat.id));
                }}
              >
                ...
              </button>
              {menuChatId === chat.id ? (
                <div className="chat-item-actions-menu" role="menu">
                  <button
                    className="chat-item-actions-option"
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
                    className="chat-item-actions-option"
                    type="button"
                    onClick={() => {
                      onArchiveChat(chat.id);
                      setMenuChatId(null);
                    }}
                  >
                    Archive
                  </button>
                  <button
                    className="chat-item-actions-option"
                    type="button"
                    onClick={() => {
                      onDownloadChat(chat.id);
                      setMenuChatId(null);
                    }}
                  >
                    Download
                  </button>
                  <button
                    type="button"
                    className="chat-item-actions-option delete"
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

      <div className="side-nav-bottom">
        <div className="side-nav-user-wrap" ref={userMenuRef}>
          <button
            className="side-nav-user user-menu-trigger"
            type="button"
            aria-expanded={userMenuOpen}
            onClick={() => setUserMenuOpen((current) => !current)}
          >
            <div className="side-nav-avatar-placeholder">LR</div>
            <div className="side-nav-user-meta">
              <strong>Local User</strong>
              <small>Step 6 controls enabled</small>
            </div>
            <div className="side-nav-user-menu-icon">...</div>
          </button>
          {userMenuOpen ? (
            <div className="user-menu-dropdown" role="menu">
              <button className="chat-item-actions-option" type="button" onClick={onOpenInfo}>
                Info
              </button>
              <button className="chat-item-actions-option" type="button" onClick={onOpenHelp}>
                Help
              </button>
              <button className="chat-item-actions-option" type="button" onClick={() => onOpenPreferences("settings")}>
                Preferences
              </button>
              <button className="chat-item-actions-option" type="button" onClick={() => onOpenPreferences("personalization")}>
                Personalization
              </button>
            </div>
          ) : null}
        </div>
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
