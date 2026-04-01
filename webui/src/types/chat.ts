export type Role = "user" | "admin";

export type CurrentUser = {
  id: number;
  username: string;
  displayname: string;
  role: Role;
  status: "active" | "inactive" | string;
  force_password_change: boolean;
};

export type AuthSession = {
  token: string;
  expires_at: string;
  max_expires_at: string;
  user: CurrentUser;
};

export type AdminUser = CurrentUser & {
  created_at: string;
  updated_at: string;
};

export type Chat = {
  id: string;
  chat_name: string;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
};

export type ChatUpdate = {
  chat_name: string;
};

export type Source = {
  chunk_id: string;
  file_name: string;
  file_path: string;
  title: string | null;
  chapter: string | null;
  section: string | null;
  page_number: number | null;
  score: number;
  tags: string[];
};

export type AttachmentMeta = {
  file_name: string;
  file_type: string;
  extraction_method: string | null;
  quality: Record<string, unknown>;
};

export type Message = {
  id: string;
  chat_id: string;
  role: "user" | "assistant";
  content: string;
  status: "pending" | "completed" | "error" | string;
  has_attachments: boolean;
  created_at: string;
  sources: Source[];
  attachments: AttachmentMeta[];
  error?: string;
};

export type MessageResponse = {
  chat_id: string;
  user_message: Message;
  assistant_message: Message;
  assistant_mode: AssistantMode;
  sources: Source[];
  attachments_used: AttachmentMeta[];
};

export type AssistantMode = "simple" | "refine";

export type Settings = {
  chat_history_messages_count: number;
  max_similarities: number;
  min_similarities: number;
  similarity_score_threshold: number;
  default_assistant_mode: AssistantMode;
  available_assistant_modes: AssistantMode[];
};

export type SettingsUpdate = {
  chat_history_messages_count: number;
  max_similarities: number;
  min_similarities: number;
  similarity_score_threshold: number;
};

export type PersonalizationBaseStyle =
  | "default"
  | "professional"
  | "friendly"
  | "direct"
  | "quirky"
  | "efficient"
  | "sceptical";

export type PersonalizationLevel = "more" | "default" | "less";

export type Personalization = {
  base_style: PersonalizationBaseStyle;
  warm: PersonalizationLevel;
  enthusiastic: PersonalizationLevel;
  headers_and_lists: PersonalizationLevel;
  custom_instructions: string;
  nickname: string;
  occupation: string;
  more_about_user: string;
};

export type PersonalizationUpdate = Personalization;

export type DownloadMessage = {
  role: "user" | "assistant" | string;
  content: string;
  created_at: string;
  sources: Source[];
  attachments: AttachmentMeta[];
};

export type ChatDownload = {
  chat_id: string;
  chat_name: string;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
  messages: DownloadMessage[];
};

export type LibraryFile = {
  id: number;
  file_name: string;
  file_path: string;
  file_type: string;
  extension: string;
  size_bytes: number;
  chunk_count: number;
  tags: string[];
  is_embedded: boolean;
  is_enabled: boolean;
  is_system: boolean;
  uploaded_by_user_id: number | null;
  can_delete: boolean;
  can_toggle_enabled: boolean;
  processing_status: string;
  updated_at: string;
};

export type LibrarySummary = {
  total_files: number;
  embedded_files: number;
  total_chunks: number;
};

export type LibraryResponse = {
  files: LibraryFile[];
  summary: LibrarySummary;
  allowed_extensions: string[];
  max_upload_files: number;
  upload_max_file_size_mb: number;
  default_tag: string;
};

export type LibraryUploadResponse = {
  files: LibraryFile[];
};

export type FilterFile = {
  file_id: number;
  file_name: string;
  file_path: string;
  tags: string[];
  global_is_enabled: boolean;
  scoped_is_enabled: boolean;
  is_enabled: boolean;
  is_locked: boolean;
  updated_at: string;
};

export type FilterFileResponse = {
  files: FilterFile[];
};

export type FilterTag = {
  tag: string;
  file_count: number;
  global_is_enabled: boolean;
  scoped_is_enabled: boolean;
  is_enabled: boolean;
  is_locked: boolean;
};

export type FilterTagResponse = {
  tags: FilterTag[];
};
