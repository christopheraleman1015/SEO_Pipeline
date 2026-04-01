import { Project } from "../lib/api";

type Props = {
  projects: Project[];
  selectedProjectId: string | null;
  onSelect: (projectId: string) => void;
};

export function ProjectList({ projects, selectedProjectId, onSelect }: Props) {
  return (
    <div className="panel">
      <div className="panel-header">
        <h2>Projects</h2>
      </div>
      <div className="project-list">
        {projects.map((project) => (
          <button
            key={project.id}
            className={project.id === selectedProjectId ? "project-card active" : "project-card"}
            onClick={() => onSelect(project.id)}
          >
            <strong>{project.name}</strong>
            <span>{project.domain}</span>
          </button>
        ))}
        {projects.length === 0 && <div className="empty">No projects yet.</div>}
      </div>
    </div>
  );
}
