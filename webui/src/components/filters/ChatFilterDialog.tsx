import type { FilterFile, FilterTag } from "../../types/chat";
import { Dialog } from "../common/Dialog";
import { FilterTables } from "./FilterTables";

type ChatFilterDialogProps = {
  chatName: string;
  files: FilterFile[];
  tags: FilterTag[];
  loading: boolean;
  error: string | null;
  busyKeys: string[];
  onClose: () => void;
  onToggleTag: (tag: FilterTag, isEnabled: boolean) => void;
  onToggleFile: (file: FilterFile, isEnabled: boolean) => void;
};

export function ChatFilterDialog({
  chatName,
  files,
  tags,
  loading,
  error,
  busyKeys,
  onClose,
  onToggleTag,
  onToggleFile,
}: ChatFilterDialogProps) {
  return (
    <Dialog
      title={`Filter ${chatName}`}
      onClose={onClose}
      actions={null}
      className="dialog-wide chat-filter-dialog"
      contentClassName="chat-filter-dialog-content"
      bodyClassName="chat-filter-dialog-body"
    >
      {error ? <p className="inline-error">{error}</p> : null}
      {loading ? (
        <div className="preferences-placeholder">Loading chat filters...</div>
      ) : (
        <FilterTables
          mode="chat"
          tags={tags}
          files={files}
          busyKeys={busyKeys}
          onToggleTag={onToggleTag}
          onToggleFile={onToggleFile}
        />
      )}
    </Dialog>
  );
}
