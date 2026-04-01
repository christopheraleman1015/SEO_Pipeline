import { useEffect, useState } from "react";
import { createProject, fetchProjects, Project } from "./lib/api";
import { ProjectForm } from "./components/ProjectForm";
import { ProjectList } from "./components/ProjectList";
import { PublisherConfigPanel } from "./components/PublisherConfigPanel";

export function App() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function loadProjects() {
    try {
      const nextProjects = await fetchProjects();
      setProjects(nextProjects);
      if (!selectedProjectId && nextProjects.length > 0) {
        setSelectedProjectId(nextProjects[0].id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load projects");
    }
  }

  useEffect(() => {
    void loadProjects();
  }, []);

  return (
    <div className="app-shell">
      <header className="hero">
        <div>
          <p className="eyebrow">SEO Pipeline</p>
          <h1>Human Control Dashboard</h1>
          <p className="subcopy">
            Configure runtime publishing, manage projects, and use the browser as the human review surface.
          </p>
        </div>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <main className="grid">
        <ProjectForm
          onSubmit={async (payload) => {
            await createProject(payload);
            await loadProjects();
          }}
        />
        <ProjectList
          projects={projects}
          selectedProjectId={selectedProjectId}
          onSelect={setSelectedProjectId}
        />
        <PublisherConfigPanel projectId={selectedProjectId} />
      </main>
    </div>
  );
}
