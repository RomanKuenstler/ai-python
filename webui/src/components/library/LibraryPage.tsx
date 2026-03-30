import { useEffect, useMemo, useState } from "react";
import type { LibraryFile, LibraryResponse } from "../../types/chat";
import { Dialog } from "../common/Dialog";
import { UploadDialog } from "./UploadDialog";

type LibraryPageProps = {
  library: LibraryResponse | null;
  loading: boolean;
  error: string | null;
  uploading: boolean;
  busyFileIds: number[];
  onLoad: () => void;
  onToggleFile: (file: LibraryFile) => void;
  onDeleteFile: (fileId: number) => void;
  onUploadFiles: (files: File[], tagsByFile: Record<string, string[]>) => Promise<void>;
};

function formatBytes(sizeBytes: number) {
  if (sizeBytes < 1024) {
    return `${sizeBytes} B`;
  }
  if (sizeBytes < 1024 * 1024) {
    return `${(sizeBytes / 1024).toFixed(1)} KB`;
  }
  return `${(sizeBytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function LibraryPage({
  library,
  loading,
  error,
  uploading,
  busyFileIds,
  onLoad,
  onToggleFile,
  onDeleteFile,
  onUploadFiles,
}: LibraryPageProps) {
  const [uploadOpen, setUploadOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<LibraryFile | null>(null);

  useEffect(() => {
    if (library === null) {
      onLoad();
    }
  }, [library, onLoad]);

  const busySet = useMemo(() => new Set(busyFileIds), [busyFileIds]);

  return (
    <section className="library-page">
      <div className="chat-header">
        <div>
          <p className="eyebrow">Managed knowledge base</p>
          <h2>Library</h2>
        </div>
        {error ? <p className="chat-error">{error}</p> : null}
      </div>

      <div className="library-summary-grid">
        <div className="summary-card">
          <span>Total files</span>
          <strong>{library?.summary.total_files ?? 0}</strong>
        </div>
        <div className="summary-card">
          <span>Embedded files</span>
          <strong>{library?.summary.embedded_files ?? 0}</strong>
        </div>
        <div className="summary-card">
          <span>Total chunks</span>
          <strong>{library?.summary.total_chunks ?? 0}</strong>
        </div>
      </div>

      <div className="library-table-shell">
        {loading ? <div className="empty-state">Loading library...</div> : null}
        {!loading && library && library.files.length === 0 ? (
          <div className="empty-state">
            <div>
              <p>No files are embedded yet.</p>
              <p>Upload supported knowledge files to start grounding answers.</p>
            </div>
          </div>
        ) : null}
        {!loading && library && library.files.length > 0 ? (
          <div className="table-scroll">
            <table className="library-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Status</th>
                  <th>Tags</th>
                  <th>Size</th>
                  <th>Chunks</th>
                  <th>Extension</th>
                  <th>Embedded</th>
                  <th>Updated</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {library.files.map((file) => (
                  <tr key={file.id}>
                    <td>{file.file_name}</td>
                    <td>
                      <span className={`status-pill ${file.is_enabled ? "enabled" : "disabled"}`}>
                        {file.is_enabled ? "Active" : "Disabled"}
                      </span>
                    </td>
                    <td>
                      <div className="tag-list">
                        {file.tags.map((tag) => (
                          <span key={tag} className="tag-pill">
                            {tag}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td>{formatBytes(file.size_bytes)}</td>
                    <td>{file.chunk_count}</td>
                    <td>
                      <span className={`extension-badge ${file.extension.replace(".", "")}`}>{file.extension || file.file_type}</span>
                    </td>
                    <td>{file.is_embedded ? "Yes" : "No"}</td>
                    <td>{new Date(file.updated_at).toLocaleString()}</td>
                    <td>
                      <div className="row-actions">
                        <button
                          className="secondary-button"
                          type="button"
                          disabled={busySet.has(file.id)}
                          onClick={() => onToggleFile(file)}
                        >
                          {file.is_enabled ? "Disable" : "Enable"}
                        </button>
                        <button
                          className="danger-button"
                          type="button"
                          disabled={busySet.has(file.id)}
                          onClick={() => setDeleteTarget(file)}
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </div>

      <div className="library-footer">
        <button className="primary-button" type="button" onClick={() => setUploadOpen(true)}>
          Upload
        </button>
      </div>

      {uploadOpen && library ? (
        <UploadDialog
          allowedExtensions={library.allowed_extensions}
          defaultTag={library.default_tag}
          maxFiles={library.max_upload_files}
          uploading={uploading}
          onClose={() => setUploadOpen(false)}
          onSubmit={onUploadFiles}
        />
      ) : null}

      {deleteTarget ? (
        <Dialog
          title="Delete File"
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
                  onDeleteFile(deleteTarget.id);
                  setDeleteTarget(null);
                }}
              >
                Delete
              </button>
            </>
          }
        >
          <p>
            Delete <strong>{deleteTarget.file_name}</strong> from the library, vector index, database, and local data folder?
          </p>
        </Dialog>
      ) : null}
    </section>
  );
}
