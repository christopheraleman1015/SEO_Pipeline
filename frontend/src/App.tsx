import { useEffect, useMemo, useState } from "react";
import { ProjectForm } from "./components/ProjectForm";
import { ProjectList } from "./components/ProjectList";
import { PublisherConfigPanel } from "./components/PublisherConfigPanel";
import {
  OpportunityBrief,
  OpportunityCluster,
  OpportunityDraft,
  OpportunityPublication,
  OpportunityReview,
  Project,
  WorkflowOverview,
  addEvidence,
  approveDraft,
  createProject,
  fetchProjects,
  fetchWorkflowBriefs,
  fetchWorkflowClusters,
  fetchWorkflowDrafts,
  fetchWorkflowLinks,
  fetchWorkflowOverview,
  fetchWorkflowPublications,
  fetchWorkflowReviews,
  publishDraft,
  triggerBrief,
  triggerClustering,
  triggerDraft,
  triggerInternalLinks,
  triggerRevision,
  triggerReview,
  triggerScoring
} from "./lib/api";

type WorkflowState = {
  overview: WorkflowOverview | null;
  clusters: OpportunityCluster[];
  briefs: OpportunityBrief[];
  drafts: OpportunityDraft[];
  reviews: OpportunityReview[];
  publications: OpportunityPublication[];
  links: Array<{
    id: string;
    source_url: string;
    target_url: string;
    suggested_anchor: string;
    score: number;
  }>;
};

const emptyWorkflow: WorkflowState = {
  overview: null,
  clusters: [],
  briefs: [],
  drafts: [],
  reviews: [],
  publications: [],
  links: []
};

function formatScore(value: number | null | undefined): string {
  if (value === null || value === undefined) return "n/a";
  return value.toFixed(3);
}

export function App() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const [workflow, setWorkflow] = useState<WorkflowState>(emptyWorkflow);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);

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

  async function loadWorkflow(projectId: string) {
    try {
      const [overview, clusters, briefs, drafts, reviews, publications, links] = await Promise.all([
        fetchWorkflowOverview(projectId),
        fetchWorkflowClusters(projectId),
        fetchWorkflowBriefs(projectId),
        fetchWorkflowDrafts(projectId),
        fetchWorkflowReviews(projectId),
        fetchWorkflowPublications(projectId),
        fetchWorkflowLinks(projectId)
      ]);
      setWorkflow({ overview, clusters, briefs, drafts, reviews, publications, links });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load workflow");
    }
  }

  useEffect(() => {
    void loadProjects();
  }, []);

  useEffect(() => {
    if (!selectedProjectId) return;
    void loadWorkflow(selectedProjectId);
  }, [selectedProjectId]);

  const selectedCluster = workflow.clusters[0] ?? null;
  const selectedBrief = useMemo(() => {
    if (!selectedCluster) return workflow.briefs[0] ?? null;
    return (
      workflow.briefs.find((brief) => brief.opportunity_cluster_id === selectedCluster.id) ??
      workflow.briefs[0] ??
      null
    );
  }, [selectedCluster, workflow.briefs]);
  const selectedDraft = useMemo(() => {
    if (!selectedBrief) return workflow.drafts[0] ?? null;
    return (
      workflow.drafts.find((draft) => draft.opportunity_brief_id === selectedBrief.id) ??
      workflow.drafts[0] ??
      null
    );
  }, [selectedBrief, workflow.drafts]);
  const selectedReview = useMemo(() => {
    if (!selectedDraft) return workflow.reviews[0] ?? null;
    return (
      workflow.reviews.find((review) => review.opportunity_draft_id === selectedDraft.id) ??
      workflow.reviews[0] ??
      null
    );
  }, [selectedDraft, workflow.reviews]);
  const selectedPublication = useMemo(() => {
    if (!selectedDraft) return workflow.publications[0] ?? null;
    return (
      workflow.publications.find((publication) => publication.opportunity_draft_id === selectedDraft.id) ??
      workflow.publications[0] ??
      null
    );
  }, [selectedDraft, workflow.publications]);

  async function runAction(label: string, action: () => Promise<unknown>) {
    if (!selectedProjectId) return;
    setStatus(`${label} started`);
    try {
      await action();
      await loadWorkflow(selectedProjectId);
      setStatus(`${label} completed`);
    } catch (err) {
      setError(err instanceof Error ? err.message : `${label} failed`);
    }
  }

  return (
    <div className="app-shell">
      <header className="hero">
        <div className="hero-copy">
          <p className="eyebrow">SEO Pipeline Control Room</p>
          <h1>Editorial Ops For Search Work</h1>
          <p className="subcopy">
            Run the pipeline, inspect the state of every artifact, attach runtime publisher config,
            and do the human decision-making inside a browser instead of the terminal.
          </p>
        </div>
        <div className="hero-metrics">
          <div className="metric-badge">
            <span>Projects</span>
            <strong>{projects.length}</strong>
          </div>
          <div className="metric-badge accent">
            <span>Selected</span>
            <strong>{selectedProjectId ? "Live" : "None"}</strong>
          </div>
        </div>
      </header>

      {(error || status) && (
        <div className={error ? "error-banner" : "status-banner"}>{error ?? status}</div>
      )}

      <section className="top-grid">
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
      </section>

      <section className="overview-grid">
        {[
          ["Opportunities", workflow.overview?.opportunities ?? 0],
          ["Clusters", workflow.overview?.clusters ?? 0],
          ["Briefs", workflow.overview?.briefs ?? 0],
          ["Drafts", workflow.overview?.drafts ?? 0],
          ["Reviews", workflow.overview?.reviews ?? 0],
          ["Publications", workflow.overview?.publications ?? 0]
        ].map(([label, value]) => (
          <article key={label} className="stat-card">
            <span>{label}</span>
            <strong>{value}</strong>
          </article>
        ))}
      </section>

      <section className="action-bar panel">
        <div className="panel-header">
          <h2>Pipeline Actions</h2>
        </div>
        <div className="action-row">
          <button disabled={!selectedProjectId} onClick={() => void runAction("Scoring", () => triggerScoring(selectedProjectId!))}>
            Score Opportunities
          </button>
          <button disabled={!selectedProjectId} onClick={() => void runAction("Clustering", () => triggerClustering(selectedProjectId!))}>
            Build Clusters
          </button>
          <button disabled={!selectedProjectId} onClick={() => void runAction("Internal Links", () => triggerInternalLinks(selectedProjectId!))}>
            Suggest Internal Links
          </button>
          <button disabled={!selectedCluster} onClick={() => void runAction("Brief", () => triggerBrief(selectedCluster!.id))}>
            Generate Brief
          </button>
          <button disabled={!selectedBrief} onClick={() => void runAction("Draft", () => triggerDraft(selectedBrief!.id))}>
            Generate Draft
          </button>
          <button disabled={!selectedDraft} onClick={() => void runAction("Review", () => triggerReview(selectedDraft!.id))}>
            Run Review
          </button>
          <button disabled={!selectedDraft} onClick={() => void runAction("Revision", () => triggerRevision(selectedDraft!.id))}>
            Revise Draft
          </button>
          <button disabled={!selectedDraft} onClick={() => void runAction("Approval", () => approveDraft(selectedDraft!.id))}>
            Approve For Publish
          </button>
          <button disabled={!selectedDraft} onClick={() => void runAction("Publish", () => publishDraft(selectedDraft!.id))}>
            Publish Draft
          </button>
        </div>
      </section>

      <section className="workflow-grid">
        <article className="panel tall-panel">
          <div className="panel-header">
            <h2>Cluster Queue</h2>
          </div>
          <div className="stack-list">
            {workflow.clusters.map((cluster) => (
              <div key={cluster.id} className={selectedCluster?.id === cluster.id ? "workflow-card selected" : "workflow-card"}>
                <div className="workflow-topline">
                  <strong>{cluster.primary_query}</strong>
                  <span>{formatScore(cluster.score)}</span>
                </div>
                <p>{cluster.query_examples}</p>
                <small>
                  {cluster.impressions} impressions • {cluster.query_count} queries
                </small>
              </div>
            ))}
            {workflow.clusters.length === 0 && <div className="empty">Run scoring and clustering to populate this lane.</div>}
          </div>
        </article>

        <article className="panel focus-panel">
          <div className="panel-header">
            <h2>Selected Brief</h2>
          </div>
          {selectedBrief ? (
            <div className="brief-view">
              <h3>{selectedBrief.brief_json.target_query}</h3>
              <p className="brief-goal">{selectedBrief.brief_json.differentiator}</p>
              <div className="pill-row">
                {selectedBrief.brief_json.schema_types.map((item) => (
                  <span key={item} className="pill">{item}</span>
                ))}
              </div>
              <div className="section-block">
                <h4>Must Cover</h4>
                <ul>
                  {selectedBrief.brief_json.must_cover_sections.map((section) => (
                    <li key={section}>{section}</li>
                  ))}
                </ul>
              </div>
              <div className="section-block">
                <h4>Evidence Required</h4>
                <ul>
                  {selectedBrief.brief_json.evidence_required.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
              <button
                onClick={() =>
                  void runAction("Evidence note", () =>
                    addEvidence(selectedBrief.id, {
                      title: "Manual evidence note",
                      content_text:
                        "Add examples, process details, and proof points here from the dashboard.",
                      evidence_type: "note"
                    })
                  )
                }
              >
                Add Placeholder Evidence Note
              </button>
            </div>
          ) : (
            <div className="empty">Generate a brief to inspect the human editing target.</div>
          )}
        </article>

        <article className="panel tall-panel">
          <div className="panel-header">
            <h2>Review Gate</h2>
          </div>
          {selectedReview ? (
            <div className="review-card">
              <div className={selectedReview.review_json.publish_ready ? "gate gate-pass" : "gate gate-fail"}>
                {selectedReview.review_json.publish_ready ? "Publish Ready" : "Needs Revision"}
              </div>
              <div className="section-block">
                <h4>Findings</h4>
                <ul>
                  {selectedReview.review_json.findings.length > 0 ? (
                    selectedReview.review_json.findings.map((finding) => <li key={finding}>{finding}</li>)
                  ) : (
                    <li>No blocking findings.</li>
                  )}
                </ul>
              </div>
              <div className="section-block">
                <h4>Revision Requirements</h4>
                <ul>
                  {selectedReview.review_json.revision_requirements.length > 0 ? (
                    selectedReview.review_json.revision_requirements.map((item) => <li key={item}>{item}</li>)
                  ) : (
                    <li>None.</li>
                  )}
                </ul>
              </div>
              <div className="section-block">
                <h4>Evidence Coverage</h4>
                <p>
                  Satisfied: {(selectedReview.review_json.satisfied_evidence_items ?? []).join(", ") || "None"}
                </p>
                <p>
                  Missing: {(selectedReview.review_json.missing_evidence_items ?? []).join(", ") || "None"}
                </p>
              </div>
            </div>
          ) : (
            <div className="empty">Run a review to see the publish gate status.</div>
          )}
        </article>
      </section>

      <section className="lower-grid">
        <article className="panel code-panel">
          <div className="panel-header">
            <h2>Latest Draft</h2>
          </div>
          {selectedDraft ? (
            <pre>{selectedDraft.content_markdown}</pre>
          ) : (
            <div className="empty">Generate a draft to inspect the output.</div>
          )}
        </article>
        <article className="panel">
          <div className="panel-header">
            <h2>Internal Link Suggestions</h2>
          </div>
          <div className="stack-list compact">
            {workflow.links.slice(0, 8).map((link) => (
              <div key={link.id} className="link-card">
                <strong>{link.suggested_anchor}</strong>
                <span>{link.source_url}</span>
                <span>→ {link.target_url}</span>
              </div>
            ))}
            {workflow.links.length === 0 && <div className="empty">Run internal link generation.</div>}
          </div>
        </article>
        <article className="panel">
          <div className="panel-header">
            <h2>Publication State</h2>
          </div>
          {selectedPublication ? (
            <div className="publication-card">
              <div className={selectedPublication.published ? "gate gate-pass" : "gate gate-neutral"}>
                {selectedPublication.published ? "Published" : "Approved Only"}
              </div>
              <p>Target URL: {selectedPublication.target_url ?? "Not assigned"}</p>
              <pre>{JSON.stringify(selectedPublication.publish_result_json, null, 2)}</pre>
            </div>
          ) : (
            <div className="empty">Approve and publish a draft to populate this panel.</div>
          )}
        </article>
      </section>
    </div>
  );
}
