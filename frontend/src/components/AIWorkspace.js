import React, { useState } from "react";

export default function AIWorkspace({ backendUrl, token }) {
  const [prompt, setPrompt] = useState("");
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const generatePlan = async () => {
    if (!prompt.trim()) return;
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`${backendUrl}/api/agent/plan`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ prompt }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Unable to generate plan");
      setPlan(data.plan);
    } catch (err) {
      setError(err.message || "Unable to generate plan");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section aria-label="AI Code Workspace">
      <h1>AI Code Workspace</h1>
      <p>Describe a change. CreatorApp24 will produce a reviewable implementation plan before edits are applied.</p>
      <textarea
        value={prompt}
        onChange={(event) => setPrompt(event.target.value)}
        placeholder="Example: Add a profile settings page with editable name and avatar"
        rows={6}
        style={{ width: "100%" }}
      />
      <button type="button" onClick={generatePlan} disabled={loading || !prompt.trim()}>
        {loading ? "Planning…" : "Generate Plan"}
      </button>
      {error && <p role="alert">{error}</p>}
      {plan && (
        <div>
          <h2>Plan</h2>
          <ol>
            {plan.steps.map((step) => (
              <li key={step.id}>
                <strong>{step.title}</strong>
                <div>{step.description}</div>
              </li>
            ))}
          </ol>
        </div>
      )}
    </section>
  );
}
