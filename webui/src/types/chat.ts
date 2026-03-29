export type Chat = {
  id: string;
  chat_name: string;
  created_at: string;
  updated_at: string;
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
