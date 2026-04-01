import type { FilterFile, FilterTag } from "../../types/chat";

type FilterTablesProps = {
  mode: "global" | "chat";
  tags: FilterTag[];
  files: FilterFile[];
  busyKeys: string[];
  showTags?: boolean;
  showFiles?: boolean;
  onToggleTag: (tag: FilterTag, isEnabled: boolean) => void;
  onToggleFile: (file: FilterFile, isEnabled: boolean) => void;
};

function Toggle({
  checked,
  disabled,
  onChange,
  label,
}: {
  checked: boolean;
  disabled?: boolean;
  onChange: () => void;
  label: string;
}) {
  return (
    <button
      type="button"
      className={`filter-toggle${checked ? " enabled" : ""}${disabled ? " disabled" : ""}`}
      role="switch"
      aria-checked={checked}
      aria-label={label}
      disabled={disabled}
      onClick={onChange}
    >
      <span className="filter-toggle-thumb" />
    </button>
  );
}

export function FilterTables({
  mode,
  tags,
  files,
  busyKeys,
  showTags = true,
  showFiles = true,
  onToggleTag,
  onToggleFile,
}: FilterTablesProps) {
  return (
    <div className="filter-panels">
      {showTags ? (
        <section className="info-group-card library-table-card filter-table-card">
          <div className="library-table-header">
            <h4>Tags</h4>
          </div>
          <div className="library-table filter-library-table filter-tag-table">
            <div className="library-table-head filter-library-head filter-tag-head">
              <span>Tag</span>
              <span>File Count</span>
              <span>Enabled</span>
            </div>
            <div className="library-table-body filter-library-body">
              {tags.map((tag) => {
                const busy = busyKeys.some((key) => key === `${mode}-tag:${tag.tag}` || key.endsWith(`:${tag.tag}`));
                return (
                  <div key={tag.tag} className={`library-table-row filter-library-row filter-tag-row${tag.is_locked ? " locked" : ""}`}>
                    <div className="filter-name-cell">
                      <strong>{tag.tag}</strong>
                      {tag.is_locked ? <span className="filter-meta">Locked by global filter</span> : null}
                    </div>
                    <div>{tag.file_count}</div>
                    <div className="filter-toggle-cell">
                      <Toggle
                        checked={tag.scoped_is_enabled}
                        disabled={busy || tag.is_locked}
                        label={`${tag.scoped_is_enabled ? "Disable" : "Enable"} tag ${tag.tag}`}
                        onChange={() => onToggleTag(tag, !tag.scoped_is_enabled)}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </section>
      ) : null}

      {showFiles ? (
        <section className="info-group-card library-table-card filter-table-card">
          <div className="library-table-header">
            <h4>Files</h4>
          </div>
          <div className="library-table filter-library-table filter-file-table">
            <div className="library-table-head filter-library-head filter-file-head">
              <span>File Name</span>
              <span>Tags</span>
              <span>Enabled</span>
            </div>
            <div className="library-table-body filter-library-body">
              {files.map((file) => {
                const busy = busyKeys.some((key) => key === `${mode}-file:${file.file_id}` || key.endsWith(`:${file.file_id}`));
                return (
                  <div key={file.file_id} className={`library-table-row filter-library-row filter-file-row${file.is_locked ? " locked" : ""}`}>
                    <div className="filter-name-cell">
                      <strong>{file.file_name}</strong>
                      {file.is_locked ? <span className="filter-meta">Locked by global file setting</span> : null}
                    </div>
                    <div className="filter-tags-cell">
                      {file.tags.length > 0 ? (
                        file.tags.map((tag) => (
                          <span key={`${file.file_id}-${tag}`} className="library-tag-line">
                            {tag}
                          </span>
                        ))
                      ) : (
                        <span className="library-tag-line muted">No tags</span>
                      )}
                    </div>
                    <div className="filter-toggle-cell">
                      <Toggle
                        checked={file.scoped_is_enabled}
                        disabled={busy || file.is_locked}
                        label={`${file.scoped_is_enabled ? "Disable" : "Enable"} file ${file.file_name}`}
                        onChange={() => onToggleFile(file, !file.scoped_is_enabled)}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </section>
      ) : null}
    </div>
  );
}
