import { FormEvent, useEffect, useState } from "react";
import { fetchPublisherConfig, savePublisherConfig } from "../lib/api";

type Props = {
  projectId: string | null;
};

export function PublisherConfigPanel({ projectId }: Props) {
  const [provider, setProvider] = useState("wordpress");
  const [mode, setMode] = useState("draft");
  const [baseUrl, setBaseUrl] = useState("");
  const [username, setUsername] = useState("");
  const [applicationPassword, setApplicationPassword] = useState("");
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!projectId) return;
    fetchPublisherConfig(projectId)
      .then((config) => {
        if (!config) return;
        setProvider(config.provider);
        setMode(config.mode);
        setBaseUrl(config.config_json.base_url ?? "");
        setUsername(config.config_json.username ?? "");
        setApplicationPassword(config.config_json.application_password ?? "");
      })
      .catch(() => setMessage("Failed to load publisher config."));
  }, [projectId]);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!projectId) return;
    await savePublisherConfig(projectId, {
      provider,
      mode,
      config_json: {
        base_url: baseUrl,
        username,
        application_password: applicationPassword
      }
    });
    setMessage("Publisher config saved.");
  }

  return (
    <form className="panel" onSubmit={handleSubmit}>
      <div className="panel-header">
        <h2>Publisher Config</h2>
      </div>
      {!projectId && <div className="empty">Select a project to configure runtime publishing.</div>}
      {projectId && (
        <>
          <label>
            Provider
            <select value={provider} onChange={(event) => setProvider(event.target.value)}>
              <option value="wordpress">WordPress</option>
              <option value="generic_rest">Generic REST</option>
            </select>
          </label>
          <label>
            Publish Mode
            <select value={mode} onChange={(event) => setMode(event.target.value)}>
              <option value="draft">Draft</option>
              <option value="live">Live</option>
            </select>
          </label>
          <label>
            Base URL
            <input value={baseUrl} onChange={(event) => setBaseUrl(event.target.value)} placeholder="https://example.com" />
          </label>
          <label>
            Username
            <input value={username} onChange={(event) => setUsername(event.target.value)} placeholder="wordpress user" />
          </label>
          <label>
            Application Password
            <input
              value={applicationPassword}
              onChange={(event) => setApplicationPassword(event.target.value)}
              placeholder="requested on demand"
            />
          </label>
          <button type="submit">Save Runtime Config</button>
          {message && <div className="note">{message}</div>}
        </>
      )}
    </form>
  );
}
