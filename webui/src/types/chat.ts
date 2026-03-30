export type Chat = {
  id: string;
  chat_name: string;
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

export type Message = {
  id: string;
  chat_id: string;
  role: "user" | "assistant";
  content: string;
  status: "pending" | "completed" | "error" | string;
  created_at: string;
  sources: Source[];
  error?: string;
};

export type MessageResponse = {
  chat_id: string;
  user_message: Message;
  assistant_message: Message;
  sources: Source[];
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
