"use client";

import React from "react";

export default function NewProjectPage() {
  const [form, setForm] = React.useState({ name: "", project_code: "", description: "", company_id: "" });
  const [loading, setLoading] = React.useState(false);
  const [message, setMessage] = React.useState(null);
  const [checkingAuth, setCheckingAuth] = React.useState(true);
  const [isAuthorized, setIsAuthorized] = React.useState(false);

  React.useEffect(() => {
    let mounted = true;
    async function check() {
      try {
        const token = window.localStorage.getItem('access_token');
        if (!token) {
          if (mounted) setIsAuthorized(false);
          return;
        }
        const res = await fetch('/api/auth/me', { headers: { Authorization: `Bearer ${token}` } });
        if (!res.ok) {
          if (mounted) setIsAuthorized(false);
          return;
        }
        const data = await res.json();
        const allowed = !!(data && (data.isSystemAdmin || data.is_system_admin));
        if (mounted) setIsAuthorized(allowed);
      } catch (err) {
        console.error('Auth check failed', err);
        if (mounted) setIsAuthorized(false);
      } finally {
        if (mounted) setCheckingAuth(false);
      }
    }
    check();
    return () => { mounted = false; };
  }, []);

  function onChange(e) {
    const { name, value } = e.target;
    setForm((s) => ({ ...s, [name]: value }));
  }

  async function onSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setMessage(null);
    try {
      const token = window.localStorage.getItem("access_token");
      const res = await fetch(`/api/projects/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : undefined
        },
        body: JSON.stringify({ project_id: form.project_code || undefined, project_name: form.name, description: form.description, location: null, client_name: null })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || JSON.stringify(data));
      setMessage({ type: "success", text: data.message || "Project created" });
      setForm({ name: "", project_code: "", description: "", company_id: "" });
    } catch (err) {
      setMessage({ type: "error", text: String(err) });
    } finally {
      setLoading(false);
    }
  }

  if (checkingAuth) {
    return <div className="p-6">Checking permissions...</div>;
  }

  if (!isAuthorized) {
    return <div className="p-6 text-red-600">Access denied. System admin privileges required.</div>;
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Create New Project</h1>
      <form onSubmit={onSubmit} className="space-y-4 max-w-xl">
        <div>
          <label className="block text-sm font-medium">Project Name</label>
          <input name="name" value={form.name} onChange={onChange} className="mt-1 block w-full" />
        </div>
        <div>
          <label className="block text-sm font-medium">Project Code (optional)</label>
          <input name="project_code" value={form.project_code} onChange={onChange} className="mt-1 block w-full" />
        </div>
        <div>
          <label className="block text-sm font-medium">Description (optional)</label>
          <textarea name="description" value={form.description} onChange={onChange} className="mt-1 block w-full" />
        </div>

        <div>
          <button disabled={loading} className="px-4 py-2 bg-blue-600 text-white rounded">{loading ? "Creating..." : "Create Project"}</button>
        </div>

        {message && (
          <div className={message.type === "error" ? "text-red-600" : "text-green-600"}>{message.text}</div>
        )}
      </form>
    </div>
  );
}
