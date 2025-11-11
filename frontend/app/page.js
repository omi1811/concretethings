'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { CheckCircle, X, Mail, Phone, MessageSquare } from 'lucide-react';

export default function Home() {
  const [showContactModal, setShowContactModal] = useState(false);
  const [contactForm, setContactForm] = useState({
    name: '',
    email: '',
    phone: '',
    company: '',
    message: '',
    projectCount: '1-5'
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  const features = [
    'Batch Tracking & Management',
    'Cube Testing & ISO Compliance',
    'Site Training Register',
    'Material Testing & Approval',
    'Third-Party Lab Integration',
    'Offline-First Architecture',
    'Real-time Sync & Updates',
    'Multi-Project Management'
  ];

  const handleContactSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    // Simulate API call (replace with actual endpoint later)
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    console.log('Contact form submitted:', contactForm);
    setSubmitSuccess(true);
    setIsSubmitting(false);
    
    // Reset and close after 2 seconds
    setTimeout(() => {
      setShowContactModal(false);
      setSubmitSuccess(false);
      setContactForm({
        name: '',
        email: '',
        phone: '',
        company: '',
        message: '',
        projectCount: '1-5'
      });
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-gray-50">
      {/* Hero section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 lg:py-24">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-blue-600 rounded-2xl mb-8">
            <span className="text-white font-bold text-3xl">CQ</span>
          </div>
          
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
            ConcreteThings QMS
          </h1>
          
          <p className="text-xl text-gray-600 mb-4 max-w-3xl mx-auto">
            Digitize Your Construction Quality Management
          </p>
          
          <p className="text-lg text-gray-500 mb-2">
            ISO Compliant • Real-time • Paperless • Works Offline
          </p>
          
          <p className="text-2xl font-bold text-blue-600 mb-8">
            ₹5,000/month per project
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/login">
              <Button size="lg" className="w-full sm:w-auto">
                Sign In
              </Button>
            </Link>
            <Button 
              size="lg" 
              variant="outline" 
              className="w-full sm:w-auto"
              onClick={() => setShowContactModal(true)}
            >
              Contact Us
            </Button>
          </div>
        </div>
        
        {/* Features grid */}
        <div className="mt-20 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <div key={index} className="flex items-start gap-3 p-4 bg-white rounded-lg shadow-sm">
              <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <span className="text-gray-900 font-medium">{feature}</span>
            </div>
          ))}
        </div>
        
        {/* Pricing */}
        <div className="mt-20 bg-white rounded-2xl shadow-lg p-8 max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-8">Simple, Transparent Pricing</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="border-2 border-gray-200 rounded-xl p-6 text-center">
              <h3 className="text-xl font-bold mb-2">Starter</h3>
              <p className="text-3xl font-bold text-blue-600 mb-4">₹5,000<span className="text-sm text-gray-600">/mo</span></p>
              <p className="text-gray-600 mb-4">1 Active Project</p>
              <ul className="text-left space-y-2 text-sm">
                <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-green-600" /> All QMS features</li>
                <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-green-600" /> Unlimited users</li>
                <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-green-600" /> Offline mode</li>
                <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-green-600" /> Email support</li>
              </ul>
            </div>
            
            <div className="border-2 border-blue-600 rounded-xl p-6 text-center bg-blue-50 relative">
              <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-blue-600 text-white px-4 py-1 rounded-full text-sm font-bold">
                POPULAR
              </div>
              <h3 className="text-xl font-bold mb-2">Professional</h3>
              <p className="text-3xl font-bold text-blue-600 mb-4">₹15,000<span className="text-sm text-gray-600">/mo</span></p>
              <p className="text-gray-600 mb-4">3-5 Active Projects</p>
              <ul className="text-left space-y-2 text-sm">
                <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-green-600" /> Everything in Starter</li>
                <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-green-600" /> Priority support</li>
                <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-green-600" /> WhatsApp integration</li>
                <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-green-600" /> Advanced analytics</li>
              </ul>
            </div>
            
            <div className="border-2 border-gray-200 rounded-xl p-6 text-center">
              <h3 className="text-xl font-bold mb-2">Enterprise</h3>
              <p className="text-3xl font-bold text-blue-600 mb-4">Custom</p>
              <p className="text-gray-600 mb-4">10+ Projects</p>
              <ul className="text-left space-y-2 text-sm">
                <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-green-600" /> Everything in Pro</li>
                <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-green-600" /> Dedicated support</li>
                <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-green-600" /> Custom branding</li>
                <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-green-600" /> API access</li>
              </ul>
            </div>
          </div>
        </div>
        
        {/* Stats */}
        <div className="mt-20 grid grid-cols-2 md:grid-cols-4 gap-8">
          <div className="text-center">
            <div className="text-4xl font-bold text-blue-600">500+</div>
            <div className="text-gray-600 mt-2">Companies</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-blue-600">10,000+</div>
            <div className="text-gray-600 mt-2">Projects</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-blue-600">100%</div>
            <div className="text-gray-600 mt-2">Offline Ready</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-blue-600">24/7</div>
            <div className="text-gray-600 mt-2">Support</div>
          </div>
        </div>
      </div>
      
      {/* Footer */}
      <footer className="border-t border-gray-200 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-gray-600">
          <p>© 2025 ConcreteThings QMS. All rights reserved.</p>
        </div>
      </footer>
      
      {/* Contact Modal */}
      {showContactModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200 flex justify-between items-center">
              <h2 className="text-2xl font-bold">Contact Us</h2>
              <button
                onClick={() => setShowContactModal(false)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            {submitSuccess ? (
              <div className="p-12 text-center">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <CheckCircle className="w-10 h-10 text-green-600" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">Thank You!</h3>
                <p className="text-gray-600">We'll get back to you within 24 hours.</p>
              </div>
            ) : (
              <form onSubmit={handleContactSubmit} className="p-6 space-y-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Full Name *
                    </label>
                    <input
                      type="text"
                      required
                      value={contactForm.name}
                      onChange={(e) => setContactForm({ ...contactForm, name: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="John Doe"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Email *
                    </label>
                    <input
                      type="email"
                      required
                      value={contactForm.email}
                      onChange={(e) => setContactForm({ ...contactForm, email: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="john@company.com"
                    />
                  </div>
                </div>
                
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Phone *
                    </label>
                    <input
                      type="tel"
                      required
                      value={contactForm.phone}
                      onChange={(e) => setContactForm({ ...contactForm, phone: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="+91 9876543210"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Company Name *
                    </label>
                    <input
                      type="text"
                      required
                      value={contactForm.company}
                      onChange={(e) => setContactForm({ ...contactForm, company: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="ABC Construction"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Number of Projects
                  </label>
                  <select
                    value={contactForm.projectCount}
                    onChange={(e) => setContactForm({ ...contactForm, projectCount: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="1-5">1-5 projects</option>
                    <option value="6-10">6-10 projects</option>
                    <option value="11-20">11-20 projects</option>
                    <option value="20+">20+ projects</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Message
                  </label>
                  <textarea
                    value={contactForm.message}
                    onChange={(e) => setContactForm({ ...contactForm, message: e.target.value })}
                    rows="4"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Tell us about your requirements..."
                  />
                </div>
                
                <div className="flex gap-3 pt-4">
                  <Button
                    type="submit"
                    disabled={isSubmitting}
                    className="flex-1"
                  >
                    {isSubmitting ? 'Sending...' : 'Send Message'}
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setShowContactModal(false)}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                </div>
                
                <div className="pt-4 border-t border-gray-200 mt-6">
                  <p className="text-sm text-gray-600 text-center mb-3">Or reach us directly:</p>
                  <div className="flex flex-col sm:flex-row justify-center gap-4 text-sm">
                    <a href="mailto:support@concretethings.com" className="flex items-center gap-2 text-blue-600 hover:text-blue-700">
                      <Mail className="w-4 h-4" />
                      support@concretethings.com
                    </a>
                    <a href="tel:+919876543210" className="flex items-center gap-2 text-blue-600 hover:text-blue-700">
                      <Phone className="w-4 h-4" />
                      +91 98765 43210
                    </a>
                    <a href="https://wa.me/919876543210" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 text-blue-600 hover:text-blue-700">
                      <MessageSquare className="w-4 h-4" />
                      WhatsApp
                    </a>
                  </div>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
