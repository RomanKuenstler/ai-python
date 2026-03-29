import { useEffect, useRef } from "react";
import type { Source } from "../../types/chat";

type SourcesPanelProps = {
  open: boolean;
  onClose: () => void;
  sources: Source[];
};

export function SourcesPanel({ open, onClose, sources }: SourcesPanelProps) {
  const ref = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!open) {
      return;
    }

    function handlePointerDown(event: MouseEvent) {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        onClose();
      }
    }

    document.addEventListener("mousedown", handlePointerDown);
    return () => document.removeEventListener("mousedown", handlePointerDown);
  }, [open, onClose]);

  if (!open) {
    return null;
  }

  return (
    <div className="sources-panel" ref={ref}>
      <div className="sources-panel-header">
        <strong>{sources.length} sources</strong>
      </div>
      <div className="sources-list">
        {sources.map((source) => (
          <article className="source-card" key={`${source.chunk_id}-${source.file_name}`}>
            <div className="source-row">
              <strong>{source.file_name}</strong>
              <span>{source.score.toFixed(3)}</span>
            </div>
            <p>{[source.title, source.chapter, source.section].filter(Boolean).join(" • ") || "Untitled chunk"}</p>
            <p className="source-path">{source.file_path}</p>
            <div className="source-meta">
              {source.page_number !== null ? <span>Page {source.page_number}</span> : null}
              {source.tags.map((tag) => (
                <span className="tag-pill" key={tag}>
                  {tag}
                </span>
              ))}
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
