export type RevisionStatus = 'pending' | 'in_progress' | 'completed' | 'rejected' | 'needs_rework' | 'approved';
export type RevisionPriority = 'low' | 'normal' | 'high' | 'urgent';

export interface Revision {
  id: number;
  project_id: number;
  revision_number: number;
  title: string;
  description: string;
  status: RevisionStatus;
  priority: RevisionPriority;
  progress: number; // 0-100
  time_spent_seconds: number;
  estimated_time?: number; // в часах
  actual_time?: number; // в часах
  created_by_id: number;
  assigned_to_id?: number;
  assigned_to_username?: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  project_title?: string;
}

export interface RevisionMessage {
  id: number;
  revision_id: number;
  sender_type: 'client' | 'executor' | 'admin';
  sender_user_id: number;
  sender_name?: string;
  message: string;
  is_internal: boolean;
  files?: RevisionMessageFile[];
  created_at: string;
}

export interface RevisionMessageFile {
  id: number;
  message_id: number;
  filename: string;
  original_filename: string;
  file_type: 'image' | 'document' | 'video' | 'other';
  file_size: number;
  file_path: string;
  file_url?: string;
}

export interface RevisionFile {
  id: number;
  revision_id: number;
  filename: string;
  original_filename: string;
  file_type: 'image' | 'document' | 'video' | 'other';
  file_size: number;
  file_path: string;
  file_url?: string;
  uploaded_by_type: 'client' | 'executor' | 'admin';
  uploaded_by_user_id: number;
  description?: string;
  created_at: string;
}

export interface CreateRevisionData {
  project_id: number;
  title: string;
  description: string;
  priority: RevisionPriority;
  files?: File[];
}

export interface RevisionStats {
  total: number;
  open: number;
  pending: number;
  in_progress: number;
  completed: number;
  needs_rework: number;
}
