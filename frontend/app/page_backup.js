'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { ArrowRight, CheckCircle, Mail, X } from 'lucide-react';

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

  const handleContactSubmit = async (event) => {
    event.preventDefault();
    setIsSubmitting(true);

    await new Promise((resolve) => setTimeout(resolve, 1000));

    setSubmitSuccess(true);
    setIsSubmitting(false);

    setTimeout(() => {
      setShowContactModal(false);
      setSubmitSuccess(false);
      setContactForm({
        name: '',
        email: '',
        phone: '',
        company: '',
        message: '',
      });
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-slate-50">
      {/* Navigation */}
      <nav className="border-b border-slate-200 bg-white/80 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-blue-600 to-blue-700 font-semibold text-white shadow-sm">
              PS
            </div>
            <span className="text-xl font-semibold text-slate-900">ProSite</span>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/login">
              <Button variant="outline" size="sm">
                Sign In
              </Button>
            </Link>
            <Button size="sm" onClick={() => setShowContactModal(true)}>
              Contact Us
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="mx-auto max-w-7xl px-4 py-24 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-5xl font-bold tracking-tight text-slate-900 sm:text-6xl lg:text-7xl">
            Professional Site Management
            <span className="block text-blue-600">for Construction Projects</span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-600">
            Comprehensive quality management, safety compliance, and project oversight—all in one powerful platform designed for construction excellence.
          </p>
          <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Link href="/login">
              <Button size="lg" className="px-8 text-base">
                Get Started
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <Button size="lg" variant="outline" className="px-8 text-base" onClick={() => setShowContactModal(true)}>
              Request Demo
            </Button>
          </div>
        </div>

        {/* Features */}
        <div className="mt-32 grid gap-8 md:grid-cols-3">
          <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100">
              <CheckCircle className="h-6 w-6 text-blue-600" />
            </div>
            <h3 className="text-xl font-semibold text-slate-900">Quality Management</h3>
            <p className="mt-2 text-slate-600">
              Track concrete batches, cube tests, and material approvals with complete traceability.
            </p>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-green-100">
              <CheckCircle className="h-6 w-6 text-green-600" />
            </div>
            <h3 className="text-xl font-semibold text-slate-900">Safety Compliance</h3>
            <p className="mt-2 text-slate-600">
              Manage permits-to-work, safety audits, and incident reporting with NCR scoring.
            </p>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-purple-100">
              <CheckCircle className="h-6 w-6 text-purple-600" />
            </div>
            <h3 className="text-xl font-semibold text-slate-900">Real-time Insights</h3>
            <p className="mt-2 text-slate-600">
              Access dashboards, analytics, and executive reports for informed decision-making.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-32 border-t border-slate-200 bg-white py-12">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-blue-600 to-blue-700 font-semibold text-white">
                PS
              </div>
              <span className="text-lg font-semibold text-slate-900">ProSite</span>
            </div>
            <p className="text-sm text-slate-600">© 2025 ProSite. All rights reserved.</p>
            <a href="mailto:shrotrio@gmail.com" className="flex items-center gap-2 text-sm text-slate-600 hover:text-slate-900">
              <Mail className="h-4 w-4" />
              shrotrio@gmail.com
            </a>
          </div>
        </div>
      </footer>

      {/* Contact Modal */}

  const primarySections = [
    {
      title: 'Dashboard',
      description:
        'Real-time KPIs, NCR alerts, and operational health across every project in a single view.',
      icon: LayoutDashboard,
      href: '/dashboard',
      cta: 'Open dashboard',
      iconClass: 'bg-blue-600 text-white',
    },
    {
      title: 'Projects',
      description:
        'Curated portfolio of active and inactive programs maintained by the system admin team.',
      icon: Building2,
      href: '#projects',
      cta: 'View projects',
      iconClass: 'bg-emerald-600 text-white',
    },
    {
      title: 'Setup / Config',
      description:
        'Provision users, vendors, and contractors with guardrails that enforce company policy.',
      icon: Settings2,
      href: '#setup',
      cta: 'Manage access',
      iconClass: 'bg-orange-500 text-white',
    },
    {
      title: 'Reports',
      description:
        'Generate compliance packs, site scorecards, and executive-ready summaries on demand.',
      icon: FileBarChart,
      href: '#reports',
      cta: 'Explore reports',
      iconClass: 'bg-indigo-600 text-white',
    },
  ];

  const projects = [
    {
      name: 'ConcreteThings',
      status: 'Active',
      description:
        'End-to-end quality management covering batch registers, cube tests, and material traceability.',
      focus: ['Batch Register', 'Cube Testing', 'Material Approvals'],
      href: '/dashboard/projects/concretethings',
    },
    {
      name: 'SafetyApp',
      status: 'Inactive',
      description:
        'Safety, PTW, and NCR scoring workflows kept ready for phased rollouts across job sites.',
      focus: ['Permit-to-Work', 'Incident Logs', 'NCR Scoring'],
      href: '/dashboard/projects/safetyapp',
    },
  ];

  const setupItems = [
    {
      name: 'User Directory',
      description:
        'Invite internal users, assign multi-project roles, and enforce fine-grained permissions.',
      icon: Users,
      highlights: ['Role-based access', 'Company hierarchy'],
      href: '/dashboard/admin/users',
      cta: 'Manage users',
    },
    {
      name: 'Vendor Registry',
      description:
        'Onboard, audit, and monitor suppliers supporting your concrete and material workflows.',
      icon: Truck,
      highlights: ['Onboarding checklists', 'Performance tracking'],
      href: '/dashboard/vendors',
      cta: 'Review vendors',
    },
    {
      name: 'Contractor Console',
      description:
        'Maintain contractor compliance, documentation, and site access in one place.',
      icon: HardHat,
      highlights: ['Compliance status', 'Document vault'],
      href: '/dashboard/contractors',
      cta: 'Open console',
    },
  ];

  const reportStreams = [
    {
      name: 'Quality Intelligence',
      description:
        'Track cube strength variance, batch performance, and material approvals over time.',
      icon: ClipboardCheck,
      insights: ['Cube rejection trend', 'Batch analytics'],
      href: '/dashboard/reports/quality',
    },
    {
      name: 'Safety & NCR',
      description:
        'Monitor incident closures, NCR scoring, and permit-to-work adherence across sites.',
      icon: ShieldCheck,
      insights: ['Open NCR list', 'PTW compliance'],
      href: '/dashboard/reports/safety',
    },
    {
      name: 'Executive Summaries',
      description:
        'Generate export-ready PDF and spreadsheet snapshots for leadership and stakeholders.',
      icon: FileText,
      insights: ['KPI rollups', 'Weekly digests'],
      href: '/dashboard/reports/executive',
    },
  ];

  const activeProjects = projects.filter((project) => project.status === 'Active').length;
  const inactiveProjects = projects.length - activeProjects;

  const navigation = [
    { label: 'Dashboard', href: '/dashboard' },
    { label: 'Projects', href: '#projects' },
    { label: 'Setup / Config', href: '#setup' },
    { label: 'Reports', href: '#reports' },
  ];

  const handleContactSubmit = async (event) => {
    event.preventDefault();
    setIsSubmitting(true);

    await new Promise((resolve) => setTimeout(resolve, 1000));

    setSubmitSuccess(true);
    setIsSubmitting(false);

    setTimeout(() => {
      setShowContactModal(false);
      setSubmitSuccess(false);
      setContactForm({
        name: '',
        email: '',
        phone: '',
        company: '',
        message: '',
      });
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="sticky top-0 z-40 border-b border-slate-200 bg-white/80 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-blue-600 to-blue-700 font-semibold text-white shadow-sm">
              PS
            </div>
            <span className="text-xl font-semibold text-slate-900">ProSite</span>
          </div>
          <div className="hidden items-center gap-6 text-sm font-medium text-slate-600 md:flex">
            {navigation.map((item) => (
              <Link key={item.label} href={item.href} className="transition-colors hover:text-slate-900">
                {item.label}
              </Link>
            ))}
          </div>
          <div className="flex items-center gap-3">
            <Link href="/login">
              <Button variant="outline" size="sm">
                Sign In
              </Button>
            </Link>
            <Button size="sm" onClick={() => setShowContactModal(true)}>
              Contact Us
            </Button>
          </div>
        </div>
      </nav>

      <main>
        <section className="relative overflow-hidden bg-gradient-to-br from-blue-50 via-white to-slate-50">
          <div
            className="absolute inset-0 -z-10 bg-grid-slate-100"
            style={{ maskImage: 'linear-gradient(0deg, white, rgba(255, 255, 255, 0.7))', WebkitMaskImage: 'linear-gradient(0deg, white, rgba(255, 255, 255, 0.7))' }}
          />
          <div className="mx-auto grid max-w-7xl items-center gap-12 px-4 py-16 sm:px-6 lg:grid-cols-2 lg:py-24">
            <div>
              <p className="inline-flex items-center gap-2 rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-700">
                <BarChart3 className="h-4 w-4" />
                Operational command centre
              </p>
              <h1 className="mt-6 text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl lg:text-6xl">
                Everything your site teams need in one workspace
              </h1>
              <p className="mt-6 max-w-2xl text-lg text-slate-600">
                Navigate seamlessly between dashboards, projects curated by the system admin, configuration tasks, and export-ready reports without leaving the home page.
              </p>
              <div className="mt-8 flex flex-col gap-4 sm:flex-row">
                <Button size="lg" className="px-7 text-base" onClick={() => setShowContactModal(true)}>
                  Request a walkthrough
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
                <Link href="/login">
                  <Button size="lg" variant="outline" className="w-full px-7 text-base sm:w-auto">
                    Launch app
                  </Button>
                </Link>
              </div>
              <div className="mt-10 grid gap-4 sm:grid-cols-2">
                <div className="rounded-xl border border-slate-200 bg-white/80 p-5 shadow-sm">
                  <p className="text-sm font-medium text-slate-500">Active projects</p>
                  <p className="mt-2 text-3xl font-semibold text-slate-900">{activeProjects}</p>
                  <p className="mt-1 text-sm text-slate-500">System admin maintained</p>
                </div>
                <div className="rounded-xl border border-slate-200 bg-white/80 p-5 shadow-sm">
                  <p className="text-sm font-medium text-slate-500">Inactive projects on standby</p>
                  <p className="mt-2 text-3xl font-semibold text-slate-900">{inactiveProjects}</p>
                  <p className="mt-1 text-sm text-slate-500">Ready for controlled rollout</p>
                </div>
              </div>
            </div>
            <div className="space-y-6">
              <p className="text-sm font-semibold uppercase tracking-wide text-slate-500">Quick modules</p>
              <div className="grid gap-4">
                {primarySections.map((section) => {
                  const Icon = section.icon;
                  return (
                    <Link
                      key={section.title}
                      href={section.href}
                      className="group flex items-start gap-4 rounded-2xl border border-slate-200 bg-white/90 p-6 shadow-sm transition hover:border-blue-300 hover:shadow-lg"
                    >
                      <span className={`flex h-12 w-12 items-center justify-center rounded-xl ${section.iconClass}`}>
                        <Icon className="h-6 w-6" />
                      </span>
                      <div className="flex-1">
                        <div className="flex items-center justify-between gap-3">
                          <h3 className="text-lg font-semibold text-slate-900 group-hover:text-blue-700">{section.title}</h3>
                          <span className="text-sm font-medium text-blue-600 opacity-0 transition-opacity group-hover:opacity-100">
                            {section.cta}
                          </span>
                        </div>
                        <p className="mt-2 text-sm text-slate-600">{section.description}</p>
                      </div>
                    </Link>
                  );
                })}
              </div>
            </div>
          </div>
        </section>

        <section id="projects" className="py-16 sm:py-20">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="flex flex-col gap-6 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <p className="text-sm font-semibold uppercase tracking-wide text-slate-500">Projects</p>
                <h2 className="mt-2 text-3xl font-bold text-slate-900">Active and inactive programs curated by system admin</h2>
                <p className="mt-2 max-w-2xl text-sm text-slate-600">
                  Every project listed here is provisioned centrally. Drill into any workspace to view statuses, workflows, and rollout notes.
                </p>
              </div>
              <Link href="/dashboard/projects">
                <Button variant="outline" className="flex items-center gap-2">
                  Go to Projects
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
            </div>
            <div className="mt-10 grid gap-6 md:grid-cols-2">
              {projects.map((project) => (
                <article
                  key={project.name}
                  className="flex h-full flex-col rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:border-blue-300 hover:shadow-lg"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600 text-white">
                          <Building2 className="h-5 w-5" />
                        </div>
                        <h3 className="text-xl font-semibold text-slate-900">{project.name}</h3>
                      </div>
                      <p className="mt-3 text-sm text-slate-600">{project.description}</p>
                    </div>
                    <span
                      className={`inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-semibold ${
                        project.status === 'Active'
                          ? 'bg-emerald-100 text-emerald-700'
                          : 'bg-amber-100 text-amber-700'
                      }`}
                    >
                      {project.status}
                    </span>
                  </div>
                  <div className="mt-6 flex flex-wrap gap-2">
                    {project.focus.map((highlight) => (
                      <span
                        key={highlight}
                        className="inline-flex items-center rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600"
                      >
                        {highlight}
                      </span>
                    ))}
                  </div>
                  <div className="mt-auto flex items-center justify-between gap-4 pt-6 text-sm text-slate-500">
                    <p>Owner: System Admin</p>
                    <Link href={project.href} className="flex items-center gap-2 font-semibold text-blue-600 hover:text-blue-700">
                      Open workspace
                      <ArrowRight className="h-4 w-4" />
                    </Link>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section id="setup" className="bg-white py-16 sm:py-20">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-sm font-semibold uppercase tracking-wide text-slate-500">Setup / Config</p>
                <h2 className="mt-2 text-3xl font-bold text-slate-900">Provision access and master data confidently</h2>
                <p className="mt-2 max-w-2xl text-sm text-slate-600">
                  Dedicated consoles to add users, manage vendor performance, and oversee contractor compliance with auditable changes.
                </p>
              </div>
            </div>
            <div className="mt-10 grid gap-6 md:grid-cols-3">
              {setupItems.map((item) => {
                const Icon = item.icon;
                return (
                  <article
                    key={item.name}
                    className="flex h-full flex-col rounded-2xl border border-slate-200 bg-slate-50 p-6 shadow-sm transition hover:border-blue-300 hover:bg-white hover:shadow-lg"
                  >
                    <span className="flex h-11 w-11 items-center justify-center rounded-lg bg-blue-600 text-white shadow-sm">
                      <Icon className="h-5 w-5" />
                    </span>
                    <h3 className="mt-4 text-lg font-semibold text-slate-900">{item.name}</h3>
                    <p className="mt-2 text-sm text-slate-600">{item.description}</p>
                    <div className="mt-4 flex flex-wrap gap-2">
                      {item.highlights.map((highlight) => (
                        <span key={highlight} className="rounded-full bg-white px-3 py-1 text-xs font-medium text-slate-600">
                          {highlight}
                        </span>
                      ))}
                    </div>
                    <div className="mt-auto pt-6">
                      <Link href={item.href} className="inline-flex items-center gap-2 text-sm font-semibold text-blue-600 hover:text-blue-700">
                        {item.cta}
                        <ArrowRight className="h-4 w-4" />
                      </Link>
                    </div>
                  </article>
                );
              })}
            </div>
          </div>
        </section>

        <section id="reports" className="py-16 sm:py-20">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-sm font-semibold uppercase tracking-wide text-slate-500">Reports</p>
                <h2 className="mt-2 text-3xl font-bold text-slate-900">Insight streams tailored for operations and leadership</h2>
                <p className="mt-2 max-w-2xl text-sm text-slate-600">
                  Spin up analytics packs without spreadsheets. Each report stream keeps stakeholders aligned with the latest field data.
                </p>
              </div>
              <Link href="/dashboard/reports">
                <Button variant="outline" className="flex items-center gap-2">
                  Browse all reports
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
            </div>
            <div className="mt-10 grid gap-6 md:grid-cols-3">
              {reportStreams.map((stream) => {
                const Icon = stream.icon;
                return (
                  <article
                    key={stream.name}
                    className="flex h-full flex-col rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:border-blue-300 hover:shadow-lg"
                  >
                    <span className="flex h-11 w-11 items-center justify-center rounded-lg bg-indigo-600 text-white shadow-sm">
                      <Icon className="h-5 w-5" />
                    </span>
                    <h3 className="mt-4 text-lg font-semibold text-slate-900">{stream.name}</h3>
                    <p className="mt-2 text-sm text-slate-600">{stream.description}</p>
                    <div className="mt-4 flex flex-wrap gap-2">
                      {stream.insights.map((insight) => (
                        <span key={insight} className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
                          {insight}
                        </span>
                      ))}
                    </div>
                    <div className="mt-auto pt-6">
                      <Link href={stream.href} className="inline-flex items-center gap-2 text-sm font-semibold text-blue-600 hover:text-blue-700">
                        Open stream
                        <ArrowRight className="h-4 w-4" />
                      </Link>
                    </div>
                  </article>
                );
              })}
            </div>
          </div>
        </section>

        <section className="bg-white py-16 sm:py-20">
          <div className="mx-auto max-w-4xl px-4 text-center sm:px-6 lg:px-8">
            <h2 className="text-3xl font-bold text-slate-900 sm:text-4xl">Need a guided rollout?</h2>
            <p className="mt-3 text-lg text-slate-600">
              Our implementation team can help migrate data, configure roles, and train field staff so you can deploy quickly across every job site.
            </p>
            <div className="mt-6 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
              <Button size="lg" className="px-8 text-base" onClick={() => setShowContactModal(true)}>
                Talk to us
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
              <Link href="/login">
                <Button size="lg" variant="outline" className="px-8 text-base">
                  Sign in to continue
                </Button>
              </Link>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-slate-200 bg-slate-100 py-12">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid gap-8 md:grid-cols-3">
            <div>
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-blue-600 to-blue-700 font-semibold text-white">
                  PS
                </div>
                <span className="text-lg font-semibold text-slate-900">ProSite</span>
              </div>
              <p className="mt-3 text-sm text-slate-600">
                Professional site management for concrete, safety, and compliance-led projects.
              </p>
            </div>
            <div>
              <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Quick links</h3>
              <div className="mt-3 space-y-2 text-sm text-slate-600">
                <Link href="/dashboard" className="block hover:text-slate-900">
                  Dashboard
                </Link>
                <Link href="/dashboard/projects" className="block hover:text-slate-900">
                  Projects
                </Link>
                <Link href="/dashboard/reports" className="block hover:text-slate-900">
                  Reports
                </Link>
              </div>
            </div>
            <div>
              <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Contact</h3>
              <div className="mt-3 space-y-2 text-sm text-slate-600">
                <a href="mailto:shrotrio@gmail.com" className="flex items-center gap-2 hover:text-slate-900">
                  <Mail className="h-4 w-4" />
                  shrotrio@gmail.com
                </a>
                <button
                  onClick={() => setShowContactModal(true)}
                  className="flex items-center gap-2 text-left hover:text-slate-900"
                >
                  Schedule a call
                  <ArrowRight className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
          <div className="mt-10 border-t border-slate-200 pt-6 text-center text-sm text-slate-500">
             2025 ProSite. All rights reserved.
          </div>
        </div>
      </footer>

      {showContactModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div
            className="relative w-full max-w-2xl overflow-y-auto rounded-2xl bg-white shadow-2xl"
            style={{ maxHeight: '90vh' }}
          >
            <div className="sticky top-0 flex items-center justify-between border-b border-slate-200 bg-white px-6 py-4">
              <h2 className="text-2xl font-semibold text-slate-900">Contact us</h2>
              <button
                onClick={() => setShowContactModal(false)}
                className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-700"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {submitSuccess ? (
              <div className="px-6 py-12 text-center">
                <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100">
                  <CheckCircle className="h-10 w-10 text-emerald-600" />
                </div>
                <h3 className="text-2xl font-semibold text-slate-900">Thank you!</h3>
                <p className="mt-2 text-sm text-slate-600">We will get back to you within 24 hours.</p>
              </div>
            ) : (
              <form onSubmit={handleContactSubmit} className="space-y-4 px-6 py-6">
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <label className="text-sm font-medium text-slate-600">Full name *</label>
                    <input
                      type="text"
                      required
                      value={contactForm.name}
                      onChange={(event) => setContactForm({ ...contactForm, name: event.target.value })}
                      className="mt-1 w-full rounded-lg border border-slate-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
                      placeholder="John Doe"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium text-slate-600">Email *</label>
                    <input
                      type="email"
                      required
                      value={contactForm.email}
                      onChange={(event) => setContactForm({ ...contactForm, email: event.target.value })}
                      className="mt-1 w-full rounded-lg border border-slate-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
                      placeholder="john@company.com"
                    />
                  </div>
                </div>
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <label className="text-sm font-medium text-slate-600">Phone *</label>
                    <input
                      type="tel"
                      required
                      value={contactForm.phone}
                      onChange={(event) => setContactForm({ ...contactForm, phone: event.target.value })}
                      className="mt-1 w-full rounded-lg border border-slate-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
                      placeholder="+91 9876543210"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium text-slate-600">Company *</label>
                    <input
                      type="text"
                      required
                      value={contactForm.company}
                      onChange={(event) => setContactForm({ ...contactForm, company: event.target.value })}
                      className="mt-1 w-full rounded-lg border border-slate-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
                      placeholder="ABC Construction"
                    />
                  </div>
                </div>
                <div>
                  <label className="text-sm font-medium text-slate-600">Message</label>
                  <textarea
                    rows={4}
                    value={contactForm.message}
                    onChange={(event) => setContactForm({ ...contactForm, message: event.target.value })}
                    className="mt-1 w-full rounded-lg border border-slate-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
                    placeholder="Tell us about your rollout goals"
                  />
                </div>
                <div className="flex gap-3 pt-4">
                  <Button type="submit" disabled={isSubmitting} className="flex-1">
                    {isSubmitting ? 'Sending...' : 'Send message'}
                  </Button>
                  <Button type="button" variant="outline" onClick={() => setShowContactModal(false)} className="flex-1">
                    Cancel
                  </Button>
                </div>
                <div className="border-t border-slate-200 pt-4 text-center text-sm text-slate-500">
                  <span>Prefer email? </span>
                  <a href="mailto:shrotrio@gmail.com" className="font-medium text-blue-600 hover:text-blue-700">
                    shrotrio@gmail.com
                  </a>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
