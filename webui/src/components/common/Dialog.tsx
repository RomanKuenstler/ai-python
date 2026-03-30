import type { ReactNode } from "react";

type DialogProps = {
  title: string;
  children: ReactNode;
  actions: ReactNode;
  onClose: () => void;
};

export function Dialog({ title, children, actions, onClose }: DialogProps) {
  return (
    <div className="dialog-backdrop panel-modal-backdrop" role="presentation" onClick={onClose}>
      <div
        className="dialog panel-modal"
        role="dialog"
        aria-modal="true"
        aria-label={title}
        onClick={(event) => event.stopPropagation()}
      >
        <div className="dialog-header panel-modal-head">
          <h3>{title}</h3>
          <button className="ghost-button panel-close" type="button" onClick={onClose} aria-label="Close dialog">
            x
          </button>
        </div>
        <div className="dialog-body panel-modal-content">{children}</div>
        <div className="dialog-actions">{actions}</div>
      </div>
    </div>
  );
}
