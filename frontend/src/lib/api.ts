const API_BASE = "http://127.0.0.1:8000";

export type Project = {
  id: string;
  name: string;
  domain: string;
  locale: string;
  timezone: string;
  cms_type: string | null;
  created_at: string;
  updated_at: string;
};

export type WorkflowOverview = {
  project_id: string;
  opportunities: number;
  clusters: number;
  briefs: number;
  drafts: number;
  reviews: number;
  internal_link_opportunities: number;
  publications: number;
};

export type OpportunityCluster = {
  id: string;
  label: string;
  normalized_url: string | null;
  query_count: number;
  clicks: number;
  impressions: number;
  ctr: number;
  avg_position: number | null;
  score: number;
  primary_query: string;
  query_examples: string;
  reason: string | null;
};

export type OpportunityBrief = {
  id: string;
  opportunity_cluster_id: string;
  target_page_id: string | null;
  version: number;
  status: string;
  brief_json: {
    target_query: string;
    cluster_label: string;
    page_goal: string;
    target_url: string | null;
    audience: string;
    title_options: string[];
    h1_options: string[];
    must_cover_sections: string[];
    internal_link_sources: Array<{ source_url: string; anchor: string; score: number }>;
    schema_types: string[];
    differentiator: string;
    evidence_required: string[];
    risks: string[];
  };
  created_at: string;
  updated_at: string;
};

export type OpportunityDraft = {
  id: string;
  opportunity_brief_id: string;
  version: number;
  status: string;
  content_markdown: string;
  qa_json: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type OpportunityReview = {
  id: string;
  opportunity_draft_id: string;
  version: number;
  status: string;
  review_json: {
    publish_ready: boolean;
    findings: string[];
    revision_requirements: string[];
    word_count: number;
    missing_sections: string[];
    evidence_items: string[];
    satisfied_evidence_items?: string[];
    missing_evidence_items?: string[];
  };
  created_at: string;
  updated_at: string;
};

export type InternalLinkOpportunity = {
  id: string;
  source_url: string;
  target_url: string;
  suggested_anchor: string;
  overlap_score: number;
  target_score: number;
  score: number;
  reason: string | null;
};

export type OpportunityPublication = {
  id: string;
  opportunity_draft_id: string;
  approved_for_publish: boolean;
  published: boolean;
  target_url: string | null;
  publish_result_json: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type PublisherConfig = {
  id: string;
  project_id: string;
  provider: string;
  mode: string;
  config_json: Record<string, string>;
  created_at: string;
  updated_at: string;
};

export type OpportunityEvidence = {
  id: string;
  opportunity_brief_id: string;
  evidence_type: string;
  title: string;
  content_text: string | null;
  metadata_json: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

async function readJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${path}`);
  }
  return response.json();
}

export function fetchProjects(): Promise<Project[]> {
  return readJson<Project[]>("/projects");
}

export function createProject(payload: {
  name: string;
  domain: string;
  locale?: string;
  timezone?: string;
  cms_type?: string | null;
}): Promise<Project> {
  return readJson<Project>("/projects", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
}

export async function fetchPublisherConfig(projectId: string): Promise<PublisherConfig | null> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/publisher-config`);
  if (response.status === 404) return null;
  if (!response.ok) {
    throw new Error("Failed to load publisher config");
  }
  return response.json();
}

export function savePublisherConfig(
  projectId: string,
  payload: { provider: string; mode: string; config_json: Record<string, string> }
): Promise<PublisherConfig> {
  return readJson<PublisherConfig>(`/projects/${projectId}/publisher-config`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
}

export function fetchWorkflowOverview(projectId: string): Promise<WorkflowOverview> {
  return readJson<WorkflowOverview>(`/projects/${projectId}/workflow/overview`);
}

export function fetchWorkflowClusters(projectId: string): Promise<OpportunityCluster[]> {
  return readJson<OpportunityCluster[]>(`/projects/${projectId}/workflow/clusters`);
}

export function fetchWorkflowBriefs(projectId: string): Promise<OpportunityBrief[]> {
  return readJson<OpportunityBrief[]>(`/projects/${projectId}/workflow/briefs`);
}

export function fetchWorkflowDrafts(projectId: string): Promise<OpportunityDraft[]> {
  return readJson<OpportunityDraft[]>(`/projects/${projectId}/workflow/drafts`);
}

export function fetchWorkflowReviews(projectId: string): Promise<OpportunityReview[]> {
  return readJson<OpportunityReview[]>(`/projects/${projectId}/workflow/reviews`);
}

export function fetchWorkflowLinks(projectId: string): Promise<InternalLinkOpportunity[]> {
  return readJson<InternalLinkOpportunity[]>(`/projects/${projectId}/workflow/internal-links`);
}

export function fetchWorkflowPublications(projectId: string): Promise<OpportunityPublication[]> {
  return readJson<OpportunityPublication[]>(`/projects/${projectId}/workflow/publications`);
}

export function triggerScoring(projectId: string): Promise<{ job_id: string }> {
  return readJson<{ job_id: string }>(`/projects/${projectId}/scoring/opportunities`, {
    method: "POST"
  });
}

export function triggerClustering(projectId: string): Promise<{ job_id: string }> {
  return readJson<{ job_id: string }>(`/projects/${projectId}/cluster-opportunities`, {
    method: "POST"
  });
}

export function triggerInternalLinks(projectId: string): Promise<{ job_id: string }> {
  return readJson<{ job_id: string }>(`/projects/${projectId}/internal-links/opportunities`, {
    method: "POST"
  });
}

export function triggerBrief(clusterId: string): Promise<{ job_id: string }> {
  return readJson<{ job_id: string }>(`/opportunity-clusters/${clusterId}/briefs`, {
    method: "POST"
  });
}

export function triggerDraft(briefId: string): Promise<{ job_id: string }> {
  return readJson<{ job_id: string }>(`/opportunity-briefs/${briefId}/drafts`, {
    method: "POST"
  });
}

export function triggerReview(draftId: string): Promise<{ job_id: string }> {
  return readJson<{ job_id: string }>(`/opportunity-drafts/${draftId}/review`, {
    method: "POST"
  });
}

export function triggerRevision(draftId: string): Promise<{ job_id: string }> {
  return readJson<{ job_id: string }>(`/opportunity-drafts/${draftId}/revise`, {
    method: "POST"
  });
}

export function approveDraft(draftId: string): Promise<OpportunityPublication> {
  return readJson<OpportunityPublication>(`/opportunity-drafts/${draftId}/approve`, {
    method: "POST"
  });
}

export function publishDraft(draftId: string): Promise<{ job_id: string }> {
  return readJson<{ job_id: string }>(`/opportunity-drafts/${draftId}/publish`, {
    method: "POST"
  });
}

export function addEvidence(
  briefId: string,
  payload: { title: string; content_text: string; evidence_type?: string }
): Promise<unknown> {
  return readJson(`/opportunity-briefs/${briefId}/evidence`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
}

export function fetchEvidence(briefId: string): Promise<OpportunityEvidence[]> {
  return readJson<OpportunityEvidence[]>(`/opportunity-briefs/${briefId}/evidence`);
}
