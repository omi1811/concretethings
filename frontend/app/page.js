'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { Input, Textarea } from '@/components/ui/Input';
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
      iconClass: 'bg-blue-100 text-blue-700',
    },
    {
      title: 'Projects',
      description: 'Curated portfolio of active and inactive programs maintained by the system admin team.',
      icon: Building2,
      href: '/dashboard/projects',
      cta: 'View projects',
      iconClass: 'bg-emerald-100 text-emerald-700',
    },
    {
      title: 'Setup / Config',
      description: 'Provision users, vendors, and contractors with guardrails that enforce company policy.',
      icon: Settings2,
      href: '/dashboard/settings',
      cta: 'Manage access',
      iconClass: 'bg-orange-100 text-orange-700',
    },
    {
      title: 'Reports',
      description: 'Generate compliance packs, site scorecards, and executive-ready summaries on demand.',
      icon: FileBarChart,
      href: '/dashboard/reports',
      cta: 'Explore reports',
      iconClass: 'bg-indigo-100 text-indigo-700',
    },
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
      setContactForm({ name: '', email: '', phone: '', company: '', message: '' });
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <nav className="sticky top-0 z-40 border-b border-border bg-background/80 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary font-bold text-primary-foreground shadow-lg shadow-primary/20">PS</div>
            <span className="text-xl font-bold tracking-tight">ProSite</span>
          </div>
          <div className="flex items-center gap-3">
            {isLoggedIn ? (
              <>
                <span className="hidden text-sm font-medium text-muted-foreground sm:inline-block">{user?.full_name || user?.email || 'User'}</span>
                <Button variant="outline" size="sm" onClick={() => { localStorage.clear(); window.location.href = '/login'; }}>Logout</Button>
              </>
            ) : (
              <>
                <Link href="/login"><Button variant="ghost" size="sm">Sign In</Button></Link>
                <Button size="sm" onClick={() => setShowContactModal(true)}>Contact Us</Button>
              </>
            )}
          </div>
        </div>
      </nav>

      <main>
        {!isLoggedIn ? (
          <section className="relative overflow-hidden bg-gradient-to-b from-background via-muted/30 to-background pt-24 pb-32">
            <div className="absolute inset-0 -z-10 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]"></div>
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
              <div className="text-center">
                <div className="inline-flex items-center rounded-full border border-primary/20 bg-primary/10 px-3 py-1 text-sm font-medium text-primary mb-8">
                  <BarChart3 className="mr-2 h-4 w-4" />
                  Professional Site Management
                </div>
                <h1 className="text-5xl font-extrabold tracking-tight text-foreground sm:text-6xl lg:text-7xl mb-6">
                  Everything your site <br className="hidden sm:block" />
                  <span className="text-primary">teams need</span>
                </h1>
                <p className="mx-auto max-w-2xl text-xl text-muted-foreground mb-10">
                  Comprehensive quality management, safety compliance, and project oversight in one powerful platform.
                </p>
                <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
                  <Link href="/login">
                    <Button size="lg" className="px-8 text-base h-12 rounded-full shadow-xl shadow-primary/20">
                      Sign In
                      <ArrowRight className="ml-2 h-5 w-5" />
                    </Button>
                  </Link>
                  <Button size="lg" variant="outline" className="px-8 text-base h-12 rounded-full" onClick={() => setShowContactModal(true)}>
                    Contact Us
                  </Button>
                </div>
              </div>
            </div>
          </section>
        ) : (
          <section className="py-16 sm:py-24">
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
              <div className="text-center mb-16">
                <h1 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl">Welcome back, {user?.full_name || 'User'}</h1>
                <p className="mt-4 text-lg text-muted-foreground">Select a section to continue</p>
              </div>

              <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
                {primarySections.map((section) => {
                  const Icon = section.icon;
                  return (
                    <Link
                      key={section.title}
                      href={section.href}
                      className="group relative overflow-hidden rounded-2xl border border-border bg-card p-8 shadow-sm transition-all hover:shadow-xl hover:border-primary/50 hover:-translate-y-1"
                    >
                      <div className="relative z-10">
                        <div className={`flex h-14 w-14 items-center justify-center rounded-xl ${section.iconClass} mb-6 transition-transform group-hover:scale-110`}>
                          <Icon className="h-7 w-7" />
                        </div>
                        <h3 className="text-xl font-bold text-foreground group-hover:text-primary transition-colors">
                          {section.title}
                        </h3>
                        <p className="mt-3 text-sm text-muted-foreground leading-relaxed">{section.description}</p>
                        <div className="mt-6 flex items-center gap-2 text-sm font-semibold text-primary">
                          {section.cta}
                          <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                        </div>
                      </div>
                    </Link>
                  );
                })}
              </div>
            </div>
          </section>
        )}
      </main>

      <footer className="border-t border-border bg-muted/30 py-12">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid gap-8 md:grid-cols-2">
            <div>
              <div className="flex items-center gap-3 mb-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary font-bold text-primary-foreground">PS</div>
                <span className="text-lg font-bold text-foreground">ProSite</span>
              </div>
              <p className="text-sm text-muted-foreground max-w-xs">Professional site management for concrete, safety, and compliance-led projects.</p>
            </div>
            <div className="md:text-right">
              <h3 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground mb-4">Contact</h3>
              <div className="space-y-2 text-sm">
                <a href="mailto:shrotrio@gmail.com" className="flex items-center gap-2 md:justify-end text-foreground hover:text-primary transition-colors"><Mail className="h-4 w-4" />shrotrio@gmail.com</a>
                <button onClick={() => setShowContactModal(true)} className="flex items-center gap-2 md:justify-end text-foreground hover:text-primary transition-colors w-full md:w-auto">Schedule a call<ArrowRight className="h-4 w-4" /></button>
              </div>
            </div>
          </div>
          <div className="mt-10 border-t border-border pt-6 text-center text-sm text-muted-foreground">© 2025 ProSite. All rights reserved.</div>
        </div>
      </footer>

      {showContactModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
          <div className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-2xl border border-border bg-card shadow-2xl animate-in zoom-in-95 duration-200">
            <div className="sticky top-0 flex items-center justify-between border-b border-border bg-card px-6 py-4 z-10">
              <h2 className="text-2xl font-semibold text-foreground">Contact us</h2>
              <button onClick={() => setShowContactModal(false)} className="rounded-lg p-2 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"><X className="h-5 w-5" /></button>
            </div>
            {submitSuccess ? (
              <div className="px-6 py-12 text-center">
                <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-100"><CheckCircle className="h-10 w-10 text-green-600" /></div>
                <h3 className="text-2xl font-semibold text-foreground">Thank you!</h3>
                <p className="mt-2 text-muted-foreground">We will get back to you within 24 hours.</p>
              </div>
            ) : (
              <form onSubmit={handleContactSubmit} className="space-y-6 px-6 py-6">
                <div className="grid gap-6 md:grid-cols-2">
                  <Input
                    label="Full name"
                    required
                    value={contactForm.name}
                    onChange={(e) => setContactForm({ ...contactForm, name: e.target.value })}
                    placeholder="John Doe"
                  />
                  <Input
                    label="Email"
                    type="email"
                    required
                    value={contactForm.email}
                    onChange={(e) => setContactForm({ ...contactForm, email: e.target.value })}
                    placeholder="john@company.com"
                  />
                </div>
                <div className="grid gap-6 md:grid-cols-2">
                  <Input
                    label="Phone"
                    type="tel"
                    required
                    value={contactForm.phone}
                    onChange={(e) => setContactForm({ ...contactForm, phone: e.target.value })}
                    placeholder="+91 9876543210"
                  />
                  <Input
                    label="Company"
                    required
                    value={contactForm.company}
                    onChange={(e) => setContactForm({ ...contactForm, company: e.target.value })}
                    placeholder="ABC Construction"
                  />
                </div>
                <Textarea
                  label="Message"
                  rows={4}
                  value={contactForm.message}
                  onChange={(e) => setContactForm({ ...contactForm, message: e.target.value })}
                  placeholder="Tell us about your rollout goals"
                />
                <div className="flex gap-3 pt-2">
                  <Button type="submit" isLoading={isSubmitting} className="flex-1">Send message</Button>
                  <Button type="button" variant="outline" onClick={() => setShowContactModal(false)} className="flex-1">Cancel</Button>
                </div>
                <div className="border-t border-border pt-4 text-center text-sm text-muted-foreground">Prefer email? <a href="mailto:shrotrio@gmail.com" className="font-medium text-primary hover:underline">shrotrio@gmail.com</a></div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
