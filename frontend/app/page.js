'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import {
  ArrowRight,
  BarChart3,
  Building2,
  CheckCircle,
  ClipboardCheck,
  FileBarChart,
  FileText,
  HardHat,
  LayoutDashboard,
  Mail,
  Settings2,
  ShieldCheck,
  Truck,
  Users,
  X,
} from 'lucide-react';

export default function Home() {
  const [showContactModal, setShowContactModal] = useState(false);
  const [contactForm, setContactForm] = useState({
    name: '',
    email: '',
    phone: '',
    company: '',
    message: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token') || localStorage.getItem('auth_token');
      const userStr = localStorage.getItem('user');
      
      if (token && userStr) {
        setIsLoggedIn(true);
        try {
          setUser(JSON.parse(userStr));
        } catch (error) {
          console.error('Error parsing user data:', error);
        }
      }
    }
  }, []);

  const primarySections = [
    {
      title: 'Dashboard',
      description: 'Real-time KPIs, NCR alerts, and operational health across every project in a single view.',
      icon: LayoutDashboard,
      href: '/dashboard',
      cta: 'Open dashboard',
      iconClass: 'bg-blue-600 text-white',
    },
    {
      title: 'Projects',
      description: 'Curated portfolio of active and inactive programs maintained by the system admin team.',
      icon: Building2,
      href: '/dashboard/projects',
      cta: 'View projects',
      iconClass: 'bg-emerald-600 text-white',
    },
    {
      title: 'Setup / Config',
      description: 'Provision users, vendors, and contractors with guardrails that enforce company policy.',
      icon: Settings2,
      href: '/dashboard/settings',
      cta: 'Manage access',
      iconClass: 'bg-orange-500 text-white',
    },
    {
      title: 'Reports',
      description: 'Generate compliance packs, site scorecards, and executive-ready summaries on demand.',
      icon: FileBarChart,
      href: '/dashboard/reports',
      cta: 'Explore reports',
      iconClass: 'bg-indigo-600 text-white',
    },
  ];

  const projects = [];

  const setupItems = [
    {
      name: 'User Directory',
      description: 'Invite internal users, assign multi-project roles, and enforce fine-grained permissions.',
      icon: Users,
      highlights: ['Role-based access', 'Company hierarchy'],
      href: '/dashboard/admin/users',
      cta: 'Manage users',
    },
    {
      name: 'Vendor Registry',
      description: 'Onboard, audit, and monitor suppliers supporting your concrete and material workflows.',
      icon: Truck,
      highlights: ['Onboarding checklists', 'Performance tracking'],
      href: '/dashboard/vendors',
      cta: 'Review vendors',
    },
    {
      name: 'Contractor Console',
      description: 'Maintain contractor compliance, documentation, and site access in one place.',
      icon: HardHat,
      highlights: ['Compliance status', 'Document vault'],
      href: '/dashboard/contractors',
      cta: 'Open console',
    },
  ];

  const reportStreams = [
    {
      name: 'Quality Intelligence',
      description: 'Track cube strength variance, batch performance, and material approvals over time.',
      icon: ClipboardCheck,
      insights: ['Cube rejection trend', 'Batch analytics'],
      href: '/dashboard/reports/quality',
    },
    {
      name: 'Safety & NCR',
      description: 'Monitor incident closures, NCR scoring, and permit-to-work adherence across sites.',
      icon: ShieldCheck,
      insights: ['Open NCR list', 'PTW compliance'],
      href: '/dashboard/reports/safety',
    },
    {
      name: 'Executive Summaries',
      description: 'Generate export-ready PDF and spreadsheet snapshots for leadership and stakeholders.',
      icon: FileText,
      insights: ['KPI rollups', 'Weekly digests'],
      href: '/dashboard/reports/executive',
    },
  ];

  const activeProjects = projects.filter((project) => project.status === 'Active').length;
  const inactiveProjects = projects.length - activeProjects;

  // Navigation removed as per request

  const handleContactSubmit = async (event) => {
    event.preventDefault();
    setIsSubmitting(true);
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setSubmitSuccess(true);
    setIsSubmitting(false);
    setTimeout(() => {
      setShowContactModal(false);
      setSubmitSuccess(false);
      setContactForm({ name: '', email: '', phone: '', company: '', message: '' });
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="sticky top-0 z-40 border-b border-slate-200 bg-white/80 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-blue-600 to-blue-700 font-semibold text-white shadow-sm">PS</div>
            <span className="text-xl font-semibold text-slate-900">ProSite</span>
          </div>
          <div className="flex items-center gap-3">
            {isLoggedIn ? (
              <>
                <span className="text-sm font-medium text-slate-700">{user?.full_name || user?.email || 'User'}</span>
                <Button variant="outline" size="sm" onClick={() => { localStorage.clear(); window.location.href = '/login'; }}>Logout</Button>
              </>
            ) : (
              <>
                <Link href="/login"><Button variant="outline" size="sm">Sign In</Button></Link>
                <Button size="sm" onClick={() => setShowContactModal(true)}>Contact Us</Button>
              </>
            )}
          </div>
        </div>
      </nav>

      <main>
        {!isLoggedIn ? (
          <section className="relative overflow-hidden bg-gradient-to-br from-blue-50 via-white to-slate-50">
            <div className="absolute inset-0 -z-10 bg-grid-slate-100 [mask-image:linear-gradient(0deg,white,rgba(255,255,255,0.7))]" />
            <div className="mx-auto max-w-7xl px-4 py-24 sm:px-6 lg:py-32">
              <div className="text-center">
                <p className="inline-flex items-center gap-2 rounded-full bg-blue-100 px-4 py-2 text-sm font-medium text-blue-700">
                  <BarChart3 className="h-4 w-4" />Professional Site Management
                </p>
                <h1 className="mt-8 text-5xl font-bold tracking-tight text-slate-900 sm:text-6xl lg:text-7xl">
                  Everything your site teams need
                </h1>
                <p className="mx-auto mt-6 max-w-2xl text-xl text-slate-600">
                  Comprehensive quality management, safety compliance, and project oversight in one powerful platform.
                </p>
                <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
                  <Link href="/login">
                    <Button size="lg" className="px-8 text-base">
                      Sign In
                      <ArrowRight className="ml-2 h-5 w-5" />
                    </Button>
                  </Link>
                  <Button size="lg" variant="outline" className="px-8 text-base" onClick={() => setShowContactModal(true)}>
                    Contact Us
                  </Button>
                </div>
              </div>
            </div>
          </section>
        ) : (
          <section className="py-16 sm:py-20">
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
              <div className="text-center">
                <h1 className="text-4xl font-bold text-slate-900 sm:text-5xl">Welcome back, {user?.full_name || 'User'}</h1>
                <p className="mt-4 text-lg text-slate-600">Select a section to continue</p>
              </div>
              
              <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
                {primarySections.map((section) => {
                  const Icon = section.icon;
                  return (
                    <Link
                      key={section.title}
                      href={section.href}
                      className="group relative overflow-hidden rounded-2xl border border-slate-200 bg-white p-8 shadow-sm transition hover:border-blue-300 hover:shadow-xl"
                    >
                      <div className="relative z-10">
                        <span className={`flex h-14 w-14 items-center justify-center rounded-xl ${section.iconClass} shadow-lg`}>
                          <Icon className="h-7 w-7" />
                        </span>
                        <h3 className="mt-6 text-2xl font-semibold text-slate-900 group-hover:text-blue-700">
                          {section.title}
                        </h3>
                        <p className="mt-3 text-sm text-slate-600">{section.description}</p>
                        <div className="mt-6 flex items-center gap-2 text-sm font-semibold text-blue-600">
                          {section.cta}
                          <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                        </div>
                      </div>
                      <div className="absolute inset-0 -z-0 bg-gradient-to-br from-blue-50/50 to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
                    </Link>
                  );
                })}
              </div>
            </div>
          </section>
        )}
      </main>

      <footer className="border-t border-slate-200 bg-slate-100 py-12">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid gap-8 md:grid-cols-2">
            <div>
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-blue-600 to-blue-700 font-semibold text-white">PS</div>
                <span className="text-lg font-semibold text-slate-900">ProSite</span>
              </div>
              <p className="mt-3 text-sm text-slate-600">Professional site management for concrete, safety, and compliance-led projects.</p>
            </div>
            <div>
              <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Contact</h3>
              <div className="mt-3 space-y-2 text-sm text-slate-600">
                <a href="mailto:shrotrio@gmail.com" className="flex items-center gap-2 hover:text-slate-900"><Mail className="h-4 w-4" />shrotrio@gmail.com</a>
                <button onClick={() => setShowContactModal(true)} className="flex items-center gap-2 text-left hover:text-slate-900">Schedule a call<ArrowRight className="h-4 w-4" /></button>
              </div>
            </div>
          </div>
          <div className="mt-10 border-t border-slate-200 pt-6 text-center text-sm text-slate-500"> 2025 ProSite. All rights reserved.</div>
        </div>
      </footer>

      {showContactModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-2xl bg-white shadow-2xl">
            <div className="sticky top-0 flex items-center justify-between border-b border-slate-200 bg-white px-6 py-4">
              <h2 className="text-2xl font-semibold text-slate-900">Contact us</h2>
              <button onClick={() => setShowContactModal(false)} className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-700"><X className="h-5 w-5" /></button>
            </div>
            {submitSuccess ? (
              <div className="px-6 py-12 text-center">
                <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100"><CheckCircle className="h-10 w-10 text-emerald-600" /></div>
                <h3 className="text-2xl font-semibold text-slate-900">Thank you!</h3>
                <p className="mt-2 text-sm text-slate-600">We will get back to you within 24 hours.</p>
              </div>
            ) : (
              <form onSubmit={handleContactSubmit} className="space-y-4 px-6 py-6">
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <label className="text-sm font-medium text-slate-600">Full name *</label>
                    <input type="text" required value={contactForm.name} onChange={(event) => setContactForm({ ...contactForm, name: event.target.value })} className="mt-1 w-full rounded-lg border border-slate-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100" placeholder="John Doe" />
                  </div>
                  <div>
                    <label className="text-sm font-medium text-slate-600">Email *</label>
                    <input type="email" required value={contactForm.email} onChange={(event) => setContactForm({ ...contactForm, email: event.target.value })} className="mt-1 w-full rounded-lg border border-slate-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100" placeholder="john@company.com" />
                  </div>
                </div>
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <label className="text-sm font-medium text-slate-600">Phone *</label>
                    <input type="tel" required value={contactForm.phone} onChange={(event) => setContactForm({ ...contactForm, phone: event.target.value })} className="mt-1 w-full rounded-lg border border-slate-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100" placeholder="+91 9876543210" />
                  </div>
                  <div>
                    <label className="text-sm font-medium text-slate-600">Company *</label>
                    <input type="text" required value={contactForm.company} onChange={(event) => setContactForm({ ...contactForm, company: event.target.value })} className="mt-1 w-full rounded-lg border border-slate-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100" placeholder="ABC Construction" />
                  </div>
                </div>
                <div>
                  <label className="text-sm font-medium text-slate-600">Message</label>
                  <textarea rows={4} value={contactForm.message} onChange={(event) => setContactForm({ ...contactForm, message: event.target.value })} className="mt-1 w-full rounded-lg border border-slate-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100" placeholder="Tell us about your rollout goals" />
                </div>
                <div className="flex gap-3 pt-4">
                  <Button type="submit" disabled={isSubmitting} className="flex-1">{isSubmitting ? 'Sending...' : 'Send message'}</Button>
                  <Button type="button" variant="outline" onClick={() => setShowContactModal(false)} className="flex-1">Cancel</Button>
                </div>
                <div className="border-t border-slate-200 pt-4 text-center text-sm text-slate-500">Prefer email? <a href="mailto:shrotrio@gmail.com" className="font-medium text-blue-600 hover:text-blue-700">shrotrio@gmail.com</a></div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
