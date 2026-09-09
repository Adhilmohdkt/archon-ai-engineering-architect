export type ArchonStatus =
  | "running"
  | "human_review_required"
  | "completed"
  | "failed";

export interface ArchonRequest {
  user_goal: string;
}

export interface HumanResumeRequest {
  decision: "approve" | "revise" | "reject";
  feedback?: string;
}

export interface Critique {
  approved: boolean;
  issues: string[];
  target_agent: "requirements" | "technology" | null;
  revision_required: boolean;
}

export interface DiagramNode {
  id: string;
  label: string;
  type: string;
}

export interface DiagramEdge {
  source: string;
  target: string;
  label?: string | null;
}

export interface ArchitectureDiagram {
  nodes: DiagramNode[];
  edges: DiagramEdge[];
}

export interface ArchonResponse {
  thread_id: string;
  status: ArchonStatus;

  user_goal?: string;

  requirements?: Record<string, unknown>;
  architecture?: Record<string, unknown>;
  technologyrecommendations?: Record<string, unknown>;

  critique?: Critique;

  human_feedback?: string;
  final_blueprint?: string;

  diagram?: ArchitectureDiagram;

  error?: string;
}