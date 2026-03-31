import type { ReactNode } from "react";

type DialogProps = {
  title: string;
  children: ReactNode;
  actions: ReactNode;
  onClose: () => void;
  className?: string;
  contentClassName?: string;
  bodyClassName?: string;
  hideHeader?: boolean;
};

export function Dialog({ title, children, actions, onClose, className = "", contentClassName = "", bodyClassName = "", hideHeader = false }: DialogProps) {
  return (
    <div className="dialog-backdrop panel-modal-backdrop" role="presentation" onClick={onClose}>
      <div
        className={`dialog panel-modal ${className}`.trim()}
        role="dialog"
        aria-modal="true"
        aria-label={title}
        onClick={(event) => event.stopPropagation()}
      >
        {hideHeader ? null : (
          <div className="dialog-header panel-modal-head">
            <strong>{title}</strong>
            <button className="ghost-button panel-close" type="button" onClick={onClose} aria-label="Close dialog">
              x
            </button>
          </div>
        )}
        <div className={`dialog-body panel-modal-content ${contentClassName}`.trim()}>
          <div className={bodyClassName}>{children}</div>
        </div>
        {actions ? <div className="dialog-actions">{actions}</div> : null}
      </div>
    </div>
  );
}
