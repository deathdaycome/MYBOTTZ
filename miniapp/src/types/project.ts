export interface Project {
  id: number;
  user_id: number;
  title: string;
  description: string | null;
  original_request: string | null;
  structured_tz: Record<string, any>;
  status: ProjectStatus;
  is_archived: boolean;
  priority: Priority;
  project_type: ProjectType;
  complexity: Complexity;
  color: string;
  estimated_cost: number;
  executor_cost: number | null;
  final_cost: number | null;
  prepayment_amount: number;
  client_paid_total: number;
  executor_paid_total: number;
  estimated_hours: number;
  actual_hours: number | null;
  start_date: string;
  planned_end_date: string;
  actual_end_date: string | null;
  deadline: string | null;
  responsible_manager_id: number | null;
  created_at: string;
  updated_at: string;
  project_metadata: Record<string, any>;
  assigned_executor_id: number | null;
  assigned_at: string | null;
  test_link?: string;
}

export type ProjectStatus =
  | 'new'
  | 'review'
  | 'clarification'
  | 'proposal_sent'
  | 'accepted'
  | 'in_progress'
  | 'testing'
  | 'completed'
  | 'cancelled';

export type Priority = 'low' | 'normal' | 'high' | 'urgent';

export type ProjectType =
  | 'telegram_bot'
  | 'telegram_miniapp'
  | 'whatsapp_bot'
  | 'web_bot'
  | 'android_app'
  | 'ios_app'
  | 'integration';

export type Complexity = 'simple' | 'medium' | 'complex' | 'premium';

export interface ProjectStats {
  total: number;
  in_progress: number;
  completed: number;
  total_cost: number;
}
