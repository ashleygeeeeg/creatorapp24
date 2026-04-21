import React, { useState } from 'react';
import { Twitter, Linkedin, Github, ArrowRight, Zap, Shield, Globe, X, CheckCircle, Loader2 } from 'lucide-react';
import { joinWaitlist } from '../services/api';

const FooterSection = () => {
  const [showModal, setShowModal] = useState(false);
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email) return;
    setLoading(true);
    setError('');
    try {
      await joinWaitlist(email, name || undefined);
      setSuccess(true);
      setEmail('');
      setName('');
    } catch (err) {
      if (err.response?.status === 409) {
        setError('This email is already on the waitlist!');
      } else {
        setError('Something went wrong. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* CTA Section */}
      <section className="py-24 px-6 relative">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Start building today
          </h2>
          <p className="text-gray-500 text-lg mb-10 max-w-xl mx-auto">
            Join millions of developers and teams building the future with maligeeAi.
          </p>
          <button
            onClick={() => { setShowModal(true); setSuccess(false); setError(''); }}
            className="inline-flex items-center gap-2 px-8 py-4 bg-gray-900 hover:bg-gray-800 text-white rounded-full font-medium text-lg transition-colors duration-200 group"
          >
            Get Started Free
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-200" />
          </button>
        </div>
      </section>

      {/* Waitlist Modal */}
      {showModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4" onClick={() => setShowModal(false)}>
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" />
          <div
            className="relative bg-white rounded-2xl shadow-2xl w-full max-w-md p-8 animate-fade-in-up"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={() => setShowModal(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>

            {success ? (
              <div className="text-center py-4">
                <CheckCircle className="w-16 h-16 text-emerald-500 mx-auto mb-4" />
                <h3 className="text-2xl font-bold text-gray-900 mb-2">You're on the list!</h3>
                <p className="text-gray-500">We'll notify you when it's your turn to start building.</p>
              </div>
            ) : (
              <>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">Join the Waitlist</h3>
                <p className="text-gray-500 mb-6">Get early access to maligeeAi and start building amazing apps.</p>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Email *</label>
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="you@example.com"
                      required
                      className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Name (optional)</label>
                    <input
                      type="text"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      placeholder="Your name"
                      className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                    />
                  </div>
                  {error && <p className="text-red-500 text-sm">{error}</p>}
                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full flex items-center justify-center gap-2 px-6 py-3.5 bg-gray-900 hover:bg-gray-800 disabled:bg-gray-400 text-white rounded-full font-medium transition-colors duration-200"
                  >
                    {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Join Waitlist'}
                  </button>
                </form>
              </>
            )}
          </div>
        </div>
      )}

      {/* Trust Badges */}
      <section className="py-16 px-6 border-t border-gray-100">
        <div className="max-w-5xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="flex items-center gap-4 p-6">
              <div className="w-12 h-12 rounded-xl bg-gray-100 flex items-center justify-center">
                <Zap className="w-6 h-6 text-gray-600" />
              </div>
              <div>
                <h4 className="font-semibold text-gray-900">Lightning Fast</h4>
                <p className="text-sm text-gray-500">Deploy in seconds, not hours</p>
              </div>
            </div>
            <div className="flex items-center gap-4 p-6">
              <div className="w-12 h-12 rounded-xl bg-gray-100 flex items-center justify-center">
                <Shield className="w-6 h-6 text-gray-600" />
              </div>
              <div>
                <h4 className="font-semibold text-gray-900">Enterprise Security</h4>
                <p className="text-sm text-gray-500">SOC 2 compliant & encrypted</p>
              </div>
            </div>
            <div className="flex items-center gap-4 p-6">
              <div className="w-12 h-12 rounded-xl bg-gray-100 flex items-center justify-center">
                <Globe className="w-6 h-6 text-gray-600" />
              </div>
              <div>
                <h4 className="font-semibold text-gray-900">Global Scale</h4>
                <p className="text-sm text-gray-500">CDN-backed worldwide delivery</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 py-12 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-6">
              <span
                className="text-xl font-medium tracking-tight"
                style={{ fontFamily: "'DM Serif Display', Georgia, serif" }}
              >
                maligeeAi
              </span>
              <span className="text-sm text-gray-400">
                © 2025 maligeeAi. All rights reserved.
              </span>
            </div>
            <div className="flex items-center gap-6">
              <a href="#" className="text-sm text-gray-500 hover:text-gray-700 transition-colors">Terms</a>
              <a href="#" className="text-sm text-gray-500 hover:text-gray-700 transition-colors">Privacy</a>
              <a href="#" className="text-sm text-gray-500 hover:text-gray-700 transition-colors">Blog</a>
              <div className="flex items-center gap-3 ml-4">
                <a href="#" className="text-gray-400 hover:text-gray-600 transition-colors">
                  <Twitter className="w-4 h-4" />
                </a>
                <a href="#" className="text-gray-400 hover:text-gray-600 transition-colors">
                  <Github className="w-4 h-4" />
                </a>
                <a href="#" className="text-gray-400 hover:text-gray-600 transition-colors">
                  <Linkedin className="w-4 h-4" />
                </a>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </>
  );
};

export default FooterSection;
