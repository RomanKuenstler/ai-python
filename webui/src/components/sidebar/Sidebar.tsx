import { useEffect, useRef, useState } from "react";
import { Icon } from "../common/Icons";
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
          <span className="side-nav-item-icon">+</span>
          <span>New chat</span>
        </button>
        <button className={`side-nav-item${activeView === "library" ? " active" : ""}`} type="button" onClick={onOpenLibrary}>
          <Icon name="book" className="side-nav-item-svg" />
          <span>Library</span>
        </button>
        <button className="side-nav-item" type="button" onClick={() => onOpenPreferences("personalization")}>
          <Icon name="sparkles" className="side-nav-item-svg" />
          <span>Personalization</span>
        </button>
      </div>

      <p className="side-nav-headline">Your chats</p>

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
                <Icon name="dots" className="chat-menu-dots" />
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
                    <Icon name="edit" />
                    Rename
                  </button>
                  <button className="chat-item-actions-option" type="button" disabled>
                    <Icon name="filter" />
                    Filter
                  </button>
                  <button
                    className="chat-item-actions-option"
                    type="button"
                    onClick={() => {
                      onArchiveChat(chat.id);
                      setMenuChatId(null);
                    }}
                  >
                    <Icon name="archive" />
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
                    <Icon name="download" />
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
                    <Icon name="trash" />
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
              <strong>Test User</strong>
              <small>test</small>
            </div>
            <div className="side-nav-user-menu-icon">
              <Icon name="dots" />
            </div>
          </button>
          {userMenuOpen ? (
            <div className="user-menu-dropdown side-nav-user-menu" role="menu">
              <button className="chat-item-actions-option" type="button" onClick={onOpenInfo}>
                <Icon name="info" />
                Info
              </button>
              <button className="chat-item-actions-option" type="button" onClick={onOpenHelp}>
                <Icon name="help" />
                Help
              </button>
              <button className="chat-item-actions-option" type="button" onClick={() => onOpenPreferences("settings")}>
                <Icon name="settings" />
                Preferences
              </button>
              <button className="chat-item-actions-option" type="button" onClick={onOpenArchive}>
                <Icon name="archive" />
                Archive
              </button>
              <div className="side-nav-user-menu-divider" />
              <button className="chat-item-actions-option" type="button" disabled>
                <Icon name="key" />
                Change Password
              </button>
              <button className="chat-item-actions-option delete" type="button" disabled>
                <Icon name="logout" />
                Logout
              </button>
            </div>
          ) : null}
        </div>
      </div>

      {renameTarget ? (
        <Dialog
          title="Rename"
          onClose={() => setRenameTarget(null)}
          className="dialog-compact rename-dialog"
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
          title="Delete chat?"
          onClose={() => setDeleteTarget(null)}
          className="dialog-compact delete-chat-dialog"
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
