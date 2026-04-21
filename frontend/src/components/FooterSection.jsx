import React from 'react';
import { Twitter, Linkedin, Github, ArrowRight, Zap, Shield, Globe } from 'lucide-react';

const FooterSection = () => {
  return (
    <>
      {/* CTA Section */}
      <section className="py-24 px-6 relative">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Start building today
          </h2>
          <p className="text-gray-500 text-lg mb-10 max-w-xl mx-auto">
            Join millions of developers and teams building the future with Emergent.
          </p>
          <button className="inline-flex items-center gap-2 px-8 py-4 bg-gray-900 hover:bg-gray-800 text-white rounded-full font-medium text-lg transition-colors duration-200 group">
            Get Started Free
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-200" />
          </button>
        </div>
      </section>

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
                emergent
              </span>
              <span className="text-sm text-gray-400">
                © 2025 Emergent. All rights reserved.
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
