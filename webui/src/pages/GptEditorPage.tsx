import { useEffect, useMemo, useRef, useState, type RefObject } from "react";
import { useNavigate } from "react-router-dom";
import { apiClient } from "../api/client";
import { ChatView } from "../components/chat/ChatView";
import { Icon } from "../components/common/Icons";
import { FilterTables } from "../components/filters/FilterTables";
import { DEFAULT_GPT } from "../hooks/useChatApp";
import type { FilterFile, FilterTag, Gpt, GptUpsert, Message, Settings } from "../types/chat";

type GptEditorPageProps = {
  gptId?: string;
  settings: Settings | null;
  libraryFiles: Array<{ id: number; file_name: string; file_path: string; is_enabled: boolean; tags: string[] }>;
  attachmentRules: {
    maxFiles: number;
    allowedExtensions: string[];
  };
  onEnsureLibrary: () => Promise<void>;
  onCreate: (payload: GptUpsert) => Promise<Gpt>;
  onUpdate: (gptId: string, payload: Partial<GptUpsert>) => Promise<Gpt>;
  onPreview: (payload: { message: string; gpt: GptUpsert; preview_messages: Message[] }) => Promise<{
    user_message: Message;
    assistant_message: Message;
  }>;
};

type GptEditorSelectOption = {
  value: string;
  label: string;
  description?: string;
};

type GptEditorSelectProps = {
  id: string;
  label?: string;
  value: string;
  options: GptEditorSelectOption[];
  onChange: (nextValue: string) => void;
  openId: string | null;
  onToggle: (id: string) => void;
  onClose: () => void;
  menuRef: RefObject<HTMLDivElement>;
};

function GptEditorSelect({ id, label, value, options, onChange, openId, onToggle, onClose, menuRef }: GptEditorSelectProps) {
  const activeOption = options.find((option) => option.value === value) ?? options[0];
  const isOpen = openId === id;

  return (
    <label className="gpt-editor-field">
      {label ? <span className="gpt-editor-sublabel">{label}</span> : null}
      <div className={`gpt-editor-select header-mode-picker${isOpen ? " open" : ""}`} ref={isOpen ? menuRef : null}>
        <button
          type="button"
          className="gpt-editor-select-trigger"
          aria-expanded={isOpen}
          onClick={() => onToggle(id)}
        >
          <span className="gpt-editor-select-label">{activeOption?.label ?? value}</span>
          <Icon name="chevron-down" className="header-mode-chevron" />
        </button>
        {isOpen ? (
          <div className="gpt-editor-select-menu header-mode-menu" role="menu">
            {options.map((option) => (
              <button
                key={option.value}
                type="button"
                className={`gpt-editor-select-option header-mode-option${option.value === value ? " active" : ""}`}
                onClick={() => {
                  onChange(option.value);
                  onClose();
                }}
              >
                <span className="header-mode-option-copy">
                  <span className="gpt-editor-select-option-label">{option.label}</span>
                  {option.description ? <small>{option.description}</small> : null}
                </span>
                {option.value === value ? <Icon name="check" className="header-mode-option-check" /> : null}
              </button>
            ))}
          </div>
        ) : null}
      </div>
    </label>
  );
}

function createInitialDraft(settings: Settings | null): GptUpsert {
  return {
    ...DEFAULT_GPT,
    config: {
      ...DEFAULT_GPT.config,
      settings: {
        chat_history_messages_count: settings?.chat_history_messages_count ?? DEFAULT_GPT.config.settings.chat_history_messages_count,
        max_similarities: settings?.max_similarities ?? DEFAULT_GPT.config.settings.max_similarities,
        min_similarities: settings?.min_similarities ?? DEFAULT_GPT.config.settings.min_similarities,
        similarity_score_threshold: settings?.similarity_score_threshold ?? DEFAULT_GPT.config.settings.similarity_score_threshold,
      },
    },
  };
}

function createPreviewMessage(role: "user" | "assistant", content: string, status: Message["status"]): Message {
  return {
    id: `preview-${role}-${crypto.randomUUID()}`,
    chat_id: "preview",
    gpt_id: null,
    role,
    content,
    status,
    has_attachments: false,
    created_at: new Date().toISOString(),
    sources: [],
    attachments: [],
  };
}

export function GptEditorPage({
  gptId,
  settings,
  libraryFiles,
  attachmentRules,
  onEnsureLibrary,
  onCreate,
  onUpdate,
  onPreview,
}: GptEditorPageProps) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(Boolean(gptId));
  const [saving, setSaving] = useState(false);
  const [previewBusy, setPreviewBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [draft, setDraft] = useState<GptUpsert>(() => createInitialDraft(settings));
  const [previewMessages, setPreviewMessages] = useState<Message[]>([]);
  const [libraryRequested, setLibraryRequested] = useState(false);
  const [openSelectId, setOpenSelectId] = useState<string | null>(null);
  const selectMenuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handlePointerDown(event: MouseEvent) {
      if (selectMenuRef.current && !selectMenuRef.current.contains(event.target as Node)) {
        setOpenSelectId(null);
      }
    }

    function handleEscape(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setOpenSelectId(null);
      }
    }

    document.addEventListener("mousedown", handlePointerDown);
    document.addEventListener("keydown", handleEscape);
    return () => {
      document.removeEventListener("mousedown", handlePointerDown);
      document.removeEventListener("keydown", handleEscape);
    };
  }, []);

  useEffect(() => {
    if (libraryRequested || libraryFiles.length > 0) {
      return;
    }
    setLibraryRequested(true);
    void onEnsureLibrary();
  }, [libraryFiles.length, libraryRequested, onEnsureLibrary]);

  useEffect(() => {
    if (!gptId) {
      setDraft((current) => (current.name || current.description || current.instructions ? current : createInitialDraft(settings)));
      return;
    }
    let cancelled = false;
    setLoading(true);
    setError(null);
    void apiClient
      .getGpt(gptId)
      .then((payload) => {
        if (cancelled) {
          return;
        }
        setDraft({
          name: payload.name,
          description: payload.description,
          instructions: payload.instructions,
          assistant_mode: payload.assistant_mode,
          config: payload.config,
        });
      })
      .catch((nextError) => {
        if (!cancelled) {
          setError(nextError instanceof Error ? nextError.message : "Failed to load GPT");
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [gptId, settings]);

  const derivedTags = useMemo(() => {
    const counts = new Map<string, number>();
    libraryFiles.forEach((file) => {
      new Set(file.tags).forEach((tag) => counts.set(tag, (counts.get(tag) ?? 0) + 1));
    });
    return Array.from(counts.entries())
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([tag, fileCount]): FilterTag => {
        const override = draft.config.tag_settings.find((entry) => entry.tag === tag);
        const scoped = draft.config.tags_enabled ? override?.is_enabled ?? true : true;
        return {
          tag,
          file_count: fileCount,
          global_is_enabled: true,
          scoped_is_enabled: scoped,
          is_enabled: scoped,
          is_locked: false,
        };
      });
  }, [draft.config.tag_settings, draft.config.tags_enabled, libraryFiles]);

  const derivedFiles = useMemo(
    () =>
      libraryFiles.map<FilterFile>((file) => {
        const override = draft.config.file_settings.find((entry) => entry.file_id === file.id);
        const scoped = draft.config.files_enabled ? override?.is_enabled ?? true : true;
        return {
          file_id: file.id,
          file_name: file.file_name,
          file_path: file.file_path,
          tags: file.tags,
          global_is_enabled: file.is_enabled,
          scoped_is_enabled: scoped,
          is_enabled: file.is_enabled && scoped,
          is_locked: !file.is_enabled,
          updated_at: new Date().toISOString(),
        };
      }),
    [draft.config.file_settings, draft.config.files_enabled, libraryFiles],
  );

  const assistantModeOptions = useMemo(
    () => (settings?.available_assistant_modes ?? ["simple", "refine", "thinking"]).map((mode) => ({ value: mode, label: mode[0].toUpperCase() + mode.slice(1) })),
    [settings?.available_assistant_modes],
  );

  const baseStyleOptions = useMemo<GptEditorSelectOption[]>(
    () => ["default", "professional", "friendly", "direct", "quirky", "efficient", "sceptical"].map((value) => ({ value, label: value })),
    [],
  );

  const intensityOptions = useMemo<GptEditorSelectOption[]>(
    () => ["more", "default", "less"].map((value) => ({ value, label: value })),
    [],
  );

  function updateDraft(update: (current: GptUpsert) => GptUpsert) {
    setDraft((current) => update(current));
    setPreviewMessages([]);
  }

  function toggleSelect(id: string) {
    setOpenSelectId((current) => (current === id ? null : id));
  }

  function setFileToggle(fileId: number, isEnabled: boolean) {
    updateDraft((current) => {
      const nextEntries = current.config.file_settings.filter((entry) => entry.file_id !== fileId);
      nextEntries.push({ file_id: fileId, is_enabled: isEnabled });
      return {
        ...current,
        config: {
          ...current.config,
          file_settings: nextEntries.sort((left, right) => left.file_id - right.file_id),
        },
      };
    });
  }

  function setTagToggle(tag: string, isEnabled: boolean) {
    updateDraft((current) => {
      const nextEntries = current.config.tag_settings.filter((entry) => entry.tag !== tag);
      nextEntries.push({ tag, is_enabled: isEnabled });
      return {
        ...current,
        config: {
          ...current.config,
          tag_settings: nextEntries.sort((left, right) => left.tag.localeCompare(right.tag)),
        },
      };
    });
  }

  async function handlePreviewSend(value: string) {
    setPreviewBusy(true);
    setError(null);
    const optimisticUser = createPreviewMessage("user", value, "completed");
    const optimisticAssistant = createPreviewMessage("assistant", "Thinking...", "pending");
    setPreviewMessages((current) => [...current, optimisticUser, optimisticAssistant]);
    try {
      const response = await onPreview({
        message: value,
        gpt: draft,
        preview_messages: previewMessages,
      });
      setPreviewMessages((current) => [
        ...current.filter((message) => message.id !== optimisticUser.id && message.id !== optimisticAssistant.id),
        response.user_message,
        response.assistant_message,
      ]);
    } catch (nextError) {
      const nextMessage = nextError instanceof Error ? nextError.message : "Preview failed";
      setError(nextMessage);
      setPreviewMessages((current) => [
        ...current.filter((message) => message.id !== optimisticAssistant.id),
        {
          ...optimisticAssistant,
          content: nextMessage,
          status: "error",
          error: nextMessage,
        },
      ]);
    } finally {
      setPreviewBusy(false);
    }
  }

  async function handleSave() {
    setSaving(true);
    setError(null);
    try {
      const saved = gptId ? await onUpdate(gptId, draft) : await onCreate(draft);
      navigate(`/gpts/${saved.id}/edit`, { replace: true });
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Failed to save GPT");
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return <div className="auth-screen"><div className="auth-card"><p>Loading GPT...</p></div></div>;
  }

  return (
    <section className="gpt-editor-page">
      <header className="gpt-editor-header">
        <button className="gpt-editor-back" type="button" onClick={() => navigate(-1)}>
          Back
        </button>
        <h1 className="gpt-editor-title">{gptId ? "Edit GPT" : "New GPT"}</h1>
        <button className="primary-button gpt-editor-save" type="button" disabled={saving || !draft.name.trim()} onClick={() => void handleSave()}>
          {gptId ? "Save" : "Create"}
        </button>
      </header>

      {error ? <p className="chat-error chat-error-banner">{error}</p> : null}

      <div className="gpt-editor-layout">
        <div className="gpt-editor-panel gpt-editor-config">
          <section className="gpt-editor-section">
            <label className="gpt-editor-field">
              <span className="gpt-editor-label">Name</span>
              <input className="dialog-input" value={draft.name} placeholder="Name your GPT" onChange={(event) => updateDraft((current) => ({ ...current, name: event.target.value }))} />
            </label>
            <label className="gpt-editor-field">
              <span className="gpt-editor-label">Description</span>
              <textarea className="dialog-input preferences-textarea gpt-editor-textarea" rows={3} placeholder="Add a short description about what this GPT does" value={draft.description} onChange={(event) => updateDraft((current) => ({ ...current, description: event.target.value }))} />
            </label>
            <label className="gpt-editor-field">
              <span className="gpt-editor-label">Instructions</span>
              <textarea className="dialog-input preferences-textarea gpt-editor-textarea gpt-editor-textarea-lg" rows={6} placeholder="What does this GPT? How does it behave? What should it avoid doing?" value={draft.instructions} onChange={(event) => updateDraft((current) => ({ ...current, instructions: event.target.value }))} />
            </label>
          </section>

          <section className="gpt-editor-section">
            <h4 className="gpt-editor-section-title">Assistant Mode</h4>
            <GptEditorSelect
              id="assistant-mode"
              value={draft.assistant_mode}
              options={assistantModeOptions}
              openId={openSelectId}
              onToggle={toggleSelect}
              onClose={() => setOpenSelectId(null)}
              menuRef={selectMenuRef}
              onChange={(nextValue) => updateDraft((current) => ({ ...current, assistant_mode: nextValue as GptUpsert["assistant_mode"] }))}
            />

            <h4 className="gpt-editor-section-title">Personalization</h4>
            <div className="gpt-editor-grid">
              <GptEditorSelect
                id="base-style"
                label="Base style"
                value={draft.config.personalization.base_style}
                options={baseStyleOptions}
                openId={openSelectId}
                onToggle={toggleSelect}
                onClose={() => setOpenSelectId(null)}
                menuRef={selectMenuRef}
                onChange={(nextValue) =>
                  updateDraft((current) => ({
                    ...current,
                    config: {
                      ...current.config,
                      personalization: {
                        ...current.config.personalization,
                        base_style: nextValue as GptUpsert["config"]["personalization"]["base_style"],
                      },
                    },
                  }))
                }
              />
              {(["warm", "enthusiastic", "headers_and_lists"] as const).map((key) => (
                <GptEditorSelect
                  key={key}
                  id={`personalization-${key}`}
                  label={key.replace(/_/g, " ")}
                  value={draft.config.personalization[key]}
                  options={intensityOptions}
                  openId={openSelectId}
                  onToggle={toggleSelect}
                  onClose={() => setOpenSelectId(null)}
                  menuRef={selectMenuRef}
                  onChange={(nextValue) =>
                    updateDraft((current) => ({
                      ...current,
                      config: {
                        ...current.config,
                        personalization: { ...current.config.personalization, [key]: nextValue },
                      },
                    }))
                  }
                />
              ))}
            </div>
          </section>

          <section className="gpt-editor-section">
            <h4 className="gpt-editor-section-title">Settings</h4>
            <div className="gpt-editor-grid">
              <label className="gpt-editor-field">
                <span className="gpt-editor-sublabel">History limit</span>
                <input className="dialog-input" type="number" min={1} max={50} value={draft.config.settings.chat_history_messages_count} onChange={(event) => updateDraft((current) => ({ ...current, config: { ...current.config, settings: { ...current.config.settings, chat_history_messages_count: Number(event.target.value) } } }))} />
              </label>
              <label className="gpt-editor-field">
                <span className="gpt-editor-sublabel">Max similarities</span>
                <input className="dialog-input" type="number" min={1} max={50} value={draft.config.settings.max_similarities} onChange={(event) => updateDraft((current) => ({ ...current, config: { ...current.config, settings: { ...current.config.settings, max_similarities: Number(event.target.value) } } }))} />
              </label>
              <label className="gpt-editor-field">
                <span className="gpt-editor-sublabel">Min similarities</span>
                <input className="dialog-input" type="number" min={1} max={50} value={draft.config.settings.min_similarities} onChange={(event) => updateDraft((current) => ({ ...current, config: { ...current.config, settings: { ...current.config.settings, min_similarities: Number(event.target.value) } } }))} />
              </label>
              <label className="gpt-editor-field">
                <span className="gpt-editor-sublabel">Similarity threshold</span>
                <input className="dialog-input" type="number" min={0} max={1} step={0.05} value={draft.config.settings.similarity_score_threshold} onChange={(event) => updateDraft((current) => ({ ...current, config: { ...current.config, settings: { ...current.config.settings, similarity_score_threshold: Number(event.target.value) } } }))} />
              </label>
            </div>
          </section>

          <section className="gpt-editor-section">
            <div className="library-table-header">
              <h4 className="gpt-editor-section-title">Filters</h4>
            </div>
            <FilterTables
              mode="chat"
              tags={derivedTags}
              files={derivedFiles}
              busyKeys={[]}
              onToggleTag={(tag, isEnabled) => setTagToggle(tag.tag, isEnabled)}
              onToggleFile={(file, isEnabled) => setFileToggle(file.file_id, isEnabled)}
            />
          </section>
        </div>

        <div className="gpt-editor-panel gpt-editor-preview-shell">
          <section className="gpt-editor-preview-header">
            <div>
              <h4 className="gpt-editor-section-title">Preview</h4>
              <p className="preferences-copy">Preview resets whenever you change the GPT configuration.</p>
            </div>
          </section>
          <div className="gpt-editor-preview-pane">
            <ChatView
              messages={previewMessages}
              sending={previewBusy}
              loadingMessages={false}
              error={null}
              assistantMode={draft.assistant_mode}
              attachmentRules={attachmentRules}
              onSend={(value) => handlePreviewSend(value)}
              variant="embedded"
            />
          </div>
        </div>
      </div>
    </section>
  );
}
