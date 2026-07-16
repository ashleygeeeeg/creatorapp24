import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Plus, LogOut, MessageCircle, Rocket, DollarSign, CheckCircle, Loader2, X, Share2, Check } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DashboardPage = () => {
  const { user, logout, getAuthHeaders } = useAuth();
  const navigate = useNavigate();
  const [builds, setBuilds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showNewBuild, setShowNewBuild] = useState(false);
  const [newBuildName, setNewBuildName] = useState('');
  const [newBuildDesc, setNewBuildDesc] = useState('');
  const [creating, setCreating] = useState(false);
  const [sessions, setSessions] = useState([]);
  const [copiedBuildId, setCopiedBuildId] = useState(null);

  const fetchSessions = async () => {
    try {
      const res = await axios.get(`${API}/chat/sessions`, { headers: getAuthHeaders() });
      setSessions(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const shareBuild = async (buildId) => {
    try {
      const res = await axios.post(`${API}/builds/${buildId}/share`, {}, { headers: getAuthHeaders() });
      const link = `${window.location.origin}/share/${res.data.share_slug}`;
      try {
        await navigator.clipboard.writeText(link);
      } catch {
        window.prompt('Copy your share link:', link);
      }
      setCopiedBuildId(buildId);
      setTimeout(() => setCopiedBuildId(null), 2500);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create share link');
    }
  };

  const fetchBuilds = async () => {
    try {
      const res = await axios.get(`${API}/builds`, { headers: getAuthHeaders() });
      setBuilds(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchBuilds(); fetchSessions(); // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const createBuild = async (e) => {
    e.preventDefault();
    if (!newBuildName) return;
    setCreating(true);
    try {
      await axios.post(`${API}/builds`, { name: newBuildName, description: newBuildDesc }, { headers: getAuthHeaders() });
      setNewBuildName('');
      setNewBuildDesc('');
      setShowNewBuild(false);
      fetchBuilds();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create build');
    } finally {
      setCreating(false);
    }
  };

  const payForBuild = async (buildId) => {
    try {
      await axios.post(`${API}/builds/${buildId}/pay`, {}, { headers: getAuthHeaders() });
      fetchBuilds();
    } catch (err) {
      alert(err.response?.data?.detail || 'Payment failed');
    }
  };

  const deployBuild = async (buildId) => {
    try {
      await axios.post(`${API}/builds/${buildId}/deploy`, {}, { headers: getAuthHeaders() });
      fetchBuilds();
    } catch (err) {
      alert(err.response?.data?.detail || 'Deploy failed');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'deployed': return 'bg-emerald-100 text-emerald-700';
      case 'draft': return 'bg-gray-100 text-gray-600';
      case 'failed': return 'bg-red-100 text-red-700';
      default: return 'bg-gray-100 text-gray-600';
    }
  };

  const getPaymentBadge = (build) => {
    if (build.is_free) return <span className="text-xs px-2 py-1 rounded-full bg-emerald-100 text-emerald-700 font-medium">FREE</span>;
    if (build.payment_status === 'paid' || build.payment_status === 'mock_paid') return <span className="text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-700 font-medium">PAID</span>;
    return <span className="text-xs px-2 py-1 rounded-full bg-amber-100 text-amber-700 font-medium">$10 - UNPAID</span>;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-6">
            <h1 className="text-xl font-medium cursor-pointer" style={{ fontFamily: "'DM Serif Display', Georgia, serif" }} onClick={() => navigate('/')}>maligeeAi</h1>
            <nav className="flex items-center gap-4">
              <button onClick={() => navigate('/dashboard')} className="text-sm font-medium text-gray-900">Dashboard</button>
              <button onClick={() => navigate('/chat')} className="text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1.5 transition-colors">
                <MessageCircle className="w-4 h-4" /> Partner in Crime
              </button>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-500">{user?.email}</span>
            <button onClick={() => { logout(); navigate('/'); }} className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 transition-colors">
              <LogOut className="w-4 h-4" /> Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8">
        {/* Welcome & Stats */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900">Welcome, {user?.name || 'there'}!</h2>
          <p className="text-gray-500 mt-1">Manage your builds and deployments</p>
        </div>

        {/* Pricing Banner */}
        <div className="bg-gradient-to-r from-gray-900 to-gray-700 rounded-2xl p-6 mb-8 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold">Pricing: First build FREE, then $10/build</h3>
              <p className="text-gray-300 text-sm mt-1">All edits are free. AI Partner in Crime is always free.</p>
            </div>
            <button onClick={() => setShowNewBuild(true)} className="flex items-center gap-2 px-5 py-2.5 bg-white text-gray-900 rounded-full font-medium hover:bg-gray-100 transition-colors">
              <Plus className="w-4 h-4" /> New Build
            </button>
          </div>
        </div>

        {/* Builds Grid */}
        {loading ? (
          <div className="flex items-center justify-center py-20"><Loader2 className="w-8 h-8 animate-spin text-gray-400" /></div>
        ) : builds.length === 0 ? (
          <div className="text-center py-20">
            <div className="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-4">
              <Rocket className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No builds yet</h3>
            <p className="text-gray-500 mb-6">Your first build is FREE! Create one to get started.</p>
            <button onClick={() => setShowNewBuild(true)} className="inline-flex items-center gap-2 px-6 py-3 bg-gray-900 text-white rounded-full font-medium hover:bg-gray-800 transition-colors">
              <Plus className="w-4 h-4" /> Create Your First Build
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {builds.map(build => (
              <div key={build.id} className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-3">
                  <h4 className="font-semibold text-gray-900 truncate flex-1">{build.name}</h4>
                  {getPaymentBadge(build)}
                </div>
                {build.description && <p className="text-sm text-gray-500 mb-3 line-clamp-2">{build.description}</p>}
                <div className="flex items-center gap-2 mb-4">
                  <span className={`text-xs px-2 py-1 rounded-full font-medium capitalize ${getStatusColor(build.status)}`}>{build.status}</span>
                </div>
                <div className="flex items-center gap-2">
                  {!build.is_free && build.payment_status === 'pending' && (
                    <button onClick={() => payForBuild(build.id)} className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-gray-900 text-white rounded-lg text-sm font-medium hover:bg-gray-800 transition-colors">
                      <DollarSign className="w-3.5 h-3.5" /> Pay $10
                    </button>
                  )}
                  {(build.is_free || build.payment_status === 'paid' || build.payment_status === 'mock_paid') && build.status !== 'deployed' && (
                    <button onClick={() => deployBuild(build.id)} className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-emerald-600 text-white rounded-lg text-sm font-medium hover:bg-emerald-700 transition-colors">
                      <Rocket className="w-3.5 h-3.5" /> Deploy
                    </button>
                  )}
                  {build.status === 'deployed' && (
                    <>
                      <span className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 text-emerald-600 text-sm font-medium">
                        <CheckCircle className="w-3.5 h-3.5" /> Live
                      </span>
                      <button
                        onClick={() => shareBuild(build.id)}
                        data-testid={`share-build-btn-${build.id}`}
                        className={`flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                          copiedBuildId === build.id ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        {copiedBuildId === build.id ? (<><Check className="w-3.5 h-3.5" /> Copied!</>) : (<><Share2 className="w-3.5 h-3.5" /> Share</>)}
                      </button>
                    </>
                  )}
                </div>
                <p className="text-xs text-gray-400 mt-3">{new Date(build.created_at).toLocaleDateString()}</p>
              </div>
            ))}
          </div>
        )}

        {/* Recent Conversations */}
        <div className="mt-12" data-testid="recent-conversations-section">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-xl font-bold text-gray-900">Recent Conversations</h3>
              <p className="text-sm text-gray-500">Pick up where you left off with Partner in Crime</p>
            </div>
            <button onClick={() => navigate('/chat')} className="text-sm font-medium text-gray-700 hover:text-gray-900 flex items-center gap-1.5 transition-colors" data-testid="new-conversation-btn">
              <Plus className="w-4 h-4" /> New Conversation
            </button>
          </div>
          {sessions.length === 0 ? (
            <div className="bg-white rounded-xl border border-gray-200 p-8 text-center" data-testid="no-conversations">
              <MessageCircle className="w-8 h-8 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500 text-sm">No conversations yet. Say hi to Partner in Crime!</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {sessions.slice(0, 6).map(s => (
                <button
                  key={s.session_id}
                  onClick={() => navigate(`/chat?session=${s.session_id}`)}
                  data-testid={`conversation-card-${s.session_id}`}
                  className="bg-white rounded-xl border border-gray-200 p-4 text-left hover:shadow-md hover:border-gray-300 transition-all group"
                >
                  <div className="flex items-start gap-3">
                    <div className="w-9 h-9 rounded-full bg-violet-100 flex items-center justify-center flex-shrink-0">
                      <MessageCircle className="w-4 h-4 text-violet-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-800 truncate group-hover:text-gray-900">{s.last_message}</p>
                      <p className="text-xs text-gray-400 mt-1">{s.message_count} messages • {new Date(s.last_time).toLocaleDateString()}</p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </main>

      {/* New Build Modal */}
      {showNewBuild && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={() => setShowNewBuild(false)}>
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" />
          <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-md p-8" onClick={(e) => e.stopPropagation()}>
            <button onClick={() => setShowNewBuild(false)} className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"><X className="w-5 h-5" /></button>
            <h3 className="text-2xl font-bold text-gray-900 mb-1">New Build</h3>
            <p className="text-gray-500 text-sm mb-6">{builds.length === 0 ? 'Your first build is FREE!' : 'This build will cost $10.00'}</p>
            <form onSubmit={createBuild} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Build Name *</label>
                <input type="text" value={newBuildName} onChange={(e) => setNewBuildName(e.target.value)} placeholder="My Awesome App" required className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-gray-900 transition-all" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea value={newBuildDesc} onChange={(e) => setNewBuildDesc(e.target.value)} placeholder="What are you building?" rows={3} className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-gray-900 transition-all resize-none" />
              </div>
              <button type="submit" disabled={creating} className="w-full flex items-center justify-center gap-2 px-6 py-3.5 bg-gray-900 hover:bg-gray-800 disabled:bg-gray-400 text-white rounded-full font-medium transition-colors">
                {creating ? <Loader2 className="w-5 h-5 animate-spin" /> : (builds.length === 0 ? 'Create Free Build' : 'Create Build ($10)')}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardPage;
