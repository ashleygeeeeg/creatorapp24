import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Rocket, CheckCircle, Loader2, Sparkles, User } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SharePage = () => {
  const { slug } = useParams();
  const navigate = useNavigate();
  const [build, setBuild] = useState(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    axios.get(`${API}/share/${slug}`)
      .then(res => setBuild(res.data))
      .catch(() => setNotFound(true))
      .finally(() => setLoading(false));
  }, [slug]);

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center bg-gray-50"><Loader2 className="w-8 h-8 animate-spin text-gray-400" /></div>;
  }

  if (notFound) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 px-6 text-center" data-testid="share-not-found">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Build not found</h1>
        <p className="text-gray-500 mb-6">This share link is invalid or the build is no longer public.</p>
        <button onClick={() => navigate('/')} className="px-6 py-3 bg-gray-900 text-white rounded-full font-medium hover:bg-gray-800 transition-colors">Go to maligeeAi</button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col" data-testid="share-page">
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <h1 className="text-xl font-medium cursor-pointer" style={{ fontFamily: "'DM Serif Display', Georgia, serif" }} onClick={() => navigate('/')}>maligeeAi</h1>
          <button onClick={() => navigate('/auth')} className="px-5 py-2 bg-gray-900 text-white rounded-full text-sm font-medium hover:bg-gray-800 transition-colors" data-testid="share-cta-signup">Start building</button>
        </div>
      </header>

      <main className="flex-1 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-2xl">
          <div className="bg-white rounded-3xl border border-gray-200 shadow-xl p-10 text-center">
            <div className="w-16 h-16 rounded-2xl bg-emerald-100 flex items-center justify-center mx-auto mb-6">
              <Rocket className="w-8 h-8 text-emerald-600" />
            </div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-100 text-emerald-700 text-xs font-semibold mb-4">
              <CheckCircle className="w-3.5 h-3.5" /> LIVE
            </div>
            <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-3" data-testid="share-build-name">{build.name}</h2>
            {build.description && <p className="text-gray-500 text-base max-w-lg mx-auto mb-6" data-testid="share-build-description">{build.description}</p>}
            <div className="flex items-center justify-center gap-2 text-sm text-gray-400 mb-8">
              <User className="w-4 h-4" />
              <span data-testid="share-owner-name">Built by {build.owner_name}</span>
              <span>•</span>
              <span>{new Date(build.created_at).toLocaleDateString()}</span>
            </div>
            <div className="border-t border-gray-100 pt-8">
              <div className="flex items-center justify-center gap-2 text-gray-500 mb-4">
                <Sparkles className="w-4 h-4 text-violet-500" />
                <p className="text-sm">This app was built & deployed on maligeeAi</p>
              </div>
              <button onClick={() => navigate('/auth')} className="px-8 py-3.5 bg-gray-900 text-white rounded-full font-medium hover:bg-gray-800 transition-colors" data-testid="share-build-your-own-btn">
                Build your own — first build is FREE
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default SharePage;
