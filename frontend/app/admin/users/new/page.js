"use client";

import React from "react";

export default function NewUserPage() {
  const [form, setForm] = React.useState({
    email: "",
    phone: "",
    full_name: "",
    password: "",
    company_id: "",
    is_company_admin: false,
    is_system_admin: false
  });
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
        const res = await fetch('/api/auth/me', {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (!res.ok) {
          if (mounted) setIsAuthorized(false);
          return;
        }
        const data = await res.json();
        // backend returns camelCase isSystemAdmin
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
    const { name, value, type, checked } = e.target;
    setForm((s) => ({ ...s, [name]: type === "checkbox" ? checked : value }));
  }

  async function onSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      const token = window.localStorage.getItem("access_token");
      const res = await fetch("/api/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : undefined
        },
        body: JSON.stringify({
          email: form.email,
          phone: form.phone,
          full_name: form.full_name,
          password: form.password,
          company_id: form.company_id ? Number(form.company_id) : undefined,
          is_company_admin: form.is_company_admin,
          is_system_admin: form.is_system_admin
        })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error || JSON.stringify(data));
      setMessage({ type: "success", text: data.message || "User created" });
      setForm({ email: "", phone: "", full_name: "", password: "", company_id: "", is_company_admin: false, is_system_admin: false });
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
      <h1 className="text-2xl font-bold mb-4">Create New User</h1>
      <form onSubmit={onSubmit} className="space-y-4 max-w-xl">
        <div>
          <label className="block text-sm font-medium">Full name</label>
          <input name="full_name" value={form.full_name} onChange={onChange} className="mt-1 block w-full" />
        </div>
        <div>
          <label className="block text-sm font-medium">Email</label>
          <input name="email" value={form.email} onChange={onChange} className="mt-1 block w-full" />
        </div>
        <div>
          <label className="block text-sm font-medium">Phone</label>
          <input name="phone" value={form.phone} onChange={onChange} className="mt-1 block w-full" />
        </div>
        <div>
          <label className="block text-sm font-medium">Password</label>
          <input name="password" value={form.password} onChange={onChange} type="password" className="mt-1 block w-full" />
        </div>
        <div>
          <label className="block text-sm font-medium">Company ID (optional)</label>
          <input name="company_id" value={form.company_id} onChange={onChange} className="mt-1 block w-full" />
        </div>
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2"><input type="checkbox" name="is_company_admin" checked={form.is_company_admin} onChange={onChange} /> Company Admin</label>
          <label className="flex items-center gap-2"><input type="checkbox" name="is_system_admin" checked={form.is_system_admin} onChange={onChange} /> System Admin</label>
        </div>

        <div>
          <button disabled={loading} className="px-4 py-2 bg-blue-600 text-white rounded">{loading ? "Creating..." : "Create User"}</button>
        </div>

        {message && (
          <div className={message.type === "error" ? "text-red-600" : "text-green-600"}>{message.text}</div>
        )}
      </form>
    </div>
  );
}
