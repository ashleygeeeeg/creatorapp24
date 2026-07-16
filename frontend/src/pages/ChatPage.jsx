import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Send, ArrowLeft, Loader2, Plus, MessageCircle, Sparkles } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ChatPage = () => {
  const { user, token, getAuthHeaders } = useAuth();
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [sessions, setSessions] = useState([]);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (token) fetchSessions();
  }, [token]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchSessions = async () => {
    try {
      const res = await axios.get(`${API}/chat/sessions`, { headers: getAuthHeaders() });
      setSessions(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const loadSession = async (sid) => {
    setSessionId(sid);
    try {
      const res = await axios.get(`${API}/chat/history/${sid}`, { headers: getAuthHeaders() });
      setMessages(res.data.map(m => ({ role: m.role, content: m.content })));
    } catch (err) {
      console.error(err);
    }
  };

  const newChat = () => {
    setSessionId(null);
    setMessages([]);
    inputRef.current?.focus();
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setLoading(true);

    try {
      const headers = token ? getAuthHeaders() : {};
      const res = await axios.post(`${API}/chat`, {
        message: userMsg,
        session_id: sessionId
      }, { headers });

      setMessages(prev => [...prev, { role: 'assistant', content: res.data.response }]);
      if (!sessionId) {
        setSessionId(res.data.session_id);
        fetchSessions();
      }
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, something went wrong. Please try again.' }]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  return (
    <div className="h-screen flex bg-white">
      {/* Sidebar */}
      <div className="w-72 bg-gray-50 border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <button onClick={() => navigate('/dashboard')} className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700 mb-3 transition-colors">
            <ArrowLeft className="w-4 h-4" /> Dashboard
          </button>
          <div className="flex items-center gap-2 mb-3">
            <Sparkles className="w-5 h-5 text-violet-500" />
            <h2 className="text-lg font-bold text-gray-900">Partner in Crime</h2>
          </div>
          <button onClick={newChat} className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-gray-900 text-white rounded-xl text-sm font-medium hover:bg-gray-800 transition-colors">
            <Plus className="w-4 h-4" /> New Chat
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-2">
          {sessions.map(s => (
            <button
              key={s.session_id}
              data-testid={`chat-session-${s.session_id}`}
              onClick={() => loadSession(s.session_id)}
              className={`w-full text-left px-3 py-2.5 rounded-lg text-sm mb-1 transition-colors ${
                sessionId === s.session_id ? 'bg-gray-200 text-gray-900' : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <div className="flex items-center gap-2">
                <MessageCircle className="w-3.5 h-3.5 flex-shrink-0" />
                <span className="truncate">{s.last_message}</span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-violet-100 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-violet-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Partner in Crime</h3>
              <p className="text-xs text-gray-500">Your unfiltered AI sidekick • Always free</p>
            </div>
          </div>
          {user && <span className="text-sm text-gray-400">{user.email}</span>}
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-20 h-20 rounded-full bg-violet-100 flex items-center justify-center mb-6">
                <Sparkles className="w-10 h-10 text-violet-500" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Hey, I'm Partner in Crime</h3>
              <p className="text-gray-500 max-w-md mb-6">Your unfiltered AI sidekick. Ask me anything — I can browse the web, brainstorm ideas, explain concepts, and more. Just can't help you build until you've got a paid build.</p>
              <div className="flex flex-wrap gap-2 justify-center">
                {['What can you do?', 'Explain quantum computing', 'Help me brainstorm an app idea', 'What\'s trending in AI?'].map(q => (
                  <button key={q} onClick={() => { setInput(q); }} className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 transition-colors">
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={`flex mb-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-2xl px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-gray-900 text-white rounded-br-md'
                  : 'bg-gray-100 text-gray-800 rounded-bl-md'
              }`}>
                <div className="whitespace-pre-wrap">{msg.content}</div>
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start mb-4">
              <div className="bg-gray-100 px-4 py-3 rounded-2xl rounded-bl-md">
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <Loader2 className="w-4 h-4 animate-spin" /> Thinking...
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="px-6 py-4 border-t border-gray-200">
          <form onSubmit={sendMessage} className="flex items-center gap-3">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask Partner in Crime anything..."
              className="flex-1 px-5 py-3.5 bg-gray-100 border border-gray-200 rounded-full focus:outline-none focus:ring-2 focus:ring-gray-900 focus:bg-white transition-all"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="w-12 h-12 rounded-full bg-gray-900 hover:bg-gray-800 disabled:bg-gray-300 flex items-center justify-center transition-colors"
            >
              <Send className="w-5 h-5 text-white" />
            </button>
          </form>
          <p className="text-xs text-gray-400 text-center mt-2">Partner in Crime is free to use • Can't help build until you pay for a build</p>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
