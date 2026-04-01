import { FormEvent, useState } from "react";

type Props = {
  onSubmit: (payload: { name: string; domain: string; cms_type: string }) => Promise<void>;
};

export function ProjectForm({ onSubmit }: Props) {
  const [name, setName] = useState("");
  const [domain, setDomain] = useState("");
  const [cmsType, setCmsType] = useState("wordpress");

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!name || !domain) return;
    await onSubmit({ name, domain, cms_type: cmsType });
    setName("");
    setDomain("");
  }

  return (
    <form className="panel" onSubmit={handleSubmit}>
      <div className="panel-header">
        <h2>New Project</h2>
      </div>
      <label>
        Name
        <input value={name} onChange={(event) => setName(event.target.value)} placeholder="Client or site name" />
      </label>
      <label>
        Domain
        <input value={domain} onChange={(event) => setDomain(event.target.value)} placeholder="example.com" />
      </label>
      <label>
        CMS
        <select value={cmsType} onChange={(event) => setCmsType(event.target.value)}>
          <option value="wordpress">WordPress</option>
          <option value="generic_rest">Generic REST</option>
        </select>
      </label>
      <button type="submit">Create Project</button>
    </form>
  );
}
