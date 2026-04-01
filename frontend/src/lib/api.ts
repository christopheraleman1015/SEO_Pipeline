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

export async function fetchProjects(): Promise<Project[]> {
  const response = await fetch(`${API_BASE}/projects`);
  if (!response.ok) {
    throw new Error("Failed to load projects");
  }
  return response.json();
}

export async function createProject(payload: {
  name: string;
  domain: string;
  locale?: string;
  timezone?: string;
  cms_type?: string | null;
}): Promise<Project> {
  const response = await fetch(`${API_BASE}/projects`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error("Failed to create project");
  }
  return response.json();
}

export async function fetchPublisherConfig(projectId: string): Promise<any | null> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/publisher-config`);
  if (response.status === 404) {
    return null;
  }
  if (!response.ok) {
    throw new Error("Failed to load publisher config");
  }
  return response.json();
}

export async function savePublisherConfig(projectId: string, payload: any): Promise<any> {
  const response = await fetch(`${API_BASE}/projects/${projectId}/publisher-config`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error("Failed to save publisher config");
  }
  return response.json();
}
