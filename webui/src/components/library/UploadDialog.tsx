import { useMemo, useRef, useState, type ChangeEvent } from "react";
import { Dialog } from "../common/Dialog";

type UploadDialogProps = {
  allowedExtensions: string[];
  defaultTag: string;
  maxFiles: number;
  uploading: boolean;
  onClose: () => void;
  onSubmit: (files: File[], tagsByFile: Record<string, string[]>) => Promise<void>;
};

function normalizeTagInput(value: string, defaultTag: string) {
  const tags = value
    .split(",")
    .map((tag) => tag.trim())
    .filter(Boolean);

  return tags.length > 0 ? Array.from(new Set(tags)) : [defaultTag];
}

export function UploadDialog({ allowedExtensions, defaultTag, maxFiles, uploading, onClose, onSubmit }: UploadDialogProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [tagsByFile, setTagsByFile] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);

  const acceptValue = useMemo(() => allowedExtensions.join(","), [allowedExtensions]);

  function handleSelectFiles(event: ChangeEvent<HTMLInputElement>) {
    const nextFiles = Array.from(event.target.files ?? []);
    if (nextFiles.length === 0) {
      return;
    }

    if (nextFiles.length > maxFiles) {
      setError(`You can upload up to ${maxFiles} files at a time.`);
      return;
    }

    const invalid = nextFiles.find((file) => !allowedExtensions.includes(`.${file.name.split(".").pop()?.toLowerCase() ?? ""}`));
    if (invalid) {
      setError(`Unsupported file type: ${invalid.name}`);
      return;
    }

    const duplicates = new Set<string>();
    for (const file of nextFiles) {
      if (duplicates.has(file.name)) {
        setError(`Duplicate file selected: ${file.name}`);
        return;
      }
      duplicates.add(file.name);
    }

    setFiles(nextFiles);
    setError(null);
  }

  async function handleUpload() {
    try {
      const normalizedTags = Object.fromEntries(files.map((file) => [file.name, normalizeTagInput(tagsByFile[file.name] ?? "", defaultTag)]));
      await onSubmit(files, normalizedTags);
      onClose();
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Upload failed");
    }
  }

  return (
    <Dialog
      title="Upload Files"
      onClose={uploading ? () => undefined : onClose}
      className="dialog-compact upload-dialog-compact"
      actions={
        <>
          <button className="secondary-button" type="button" onClick={onClose} disabled={uploading}>
            Cancel
          </button>
          <button className="primary-button" type="button" onClick={() => void handleUpload()} disabled={files.length === 0 || uploading}>
            {uploading ? "Uploading..." : "Upload"}
          </button>
        </>
      }
    >
      <div className="upload-dialog-body library-upload-modal">
        {files.length === 0 ? (
          <button className="upload-picker-button library-upload-add" type="button" onClick={() => inputRef.current?.click()} disabled={uploading}>
            + Add files
          </button>
        ) : (
          <div className="upload-file-list library-upload-list">
            {files.map((file) => (
              <div key={file.name} className="upload-file-row library-upload-row">
                <div>
                  <strong className="library-upload-name">{file.name}</strong>
                  <p>{file.size.toLocaleString()} bytes</p>
                </div>
                <input
                  className="dialog-input library-upload-tags-input"
                  type="text"
                  placeholder={`Tags (comma separated, default: ${defaultTag})`}
                  value={tagsByFile[file.name] ?? ""}
                  onChange={(event) => setTagsByFile((current) => ({ ...current, [file.name]: event.target.value }))}
                  disabled={uploading}
                />
              </div>
            ))}
            <button className="secondary-button library-upload-add" type="button" onClick={() => inputRef.current?.click()} disabled={uploading}>
              + Add files
            </button>
          </div>
        )}
        <input ref={inputRef} type="file" hidden accept={acceptValue} multiple onChange={handleSelectFiles} />
        {error ? <p className="inline-error">{error}</p> : null}
      </div>
    </Dialog>
  );
}
