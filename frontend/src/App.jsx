import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { useAuth } from './hooks/useAuth';
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import ChatWidget from './components/chatbot/ChatWidget';
import { Loader2 } from 'lucide-react';

const ProtectedRoute = ({ children }) => {
    const { user, loading } = useAuth();
    
    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-[#0f172a]">
                <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
            </div>
        );
    }
    
    if (!user) {
        return <Navigate to="/login" replace />;
    }
    
    return children;
};

import HRDashboardPage from './pages/hr/HRDashboardPage';
import EmployeeDashboardPage from './pages/employee/DashboardPage';
import TeamProgressPage from './pages/manager/TeamProgressPage';

// Dynamic Dashboard Router based on role
const DashboardRouter = () => {
    const { user, logout, updateProfile } = useAuth();
    const [isSettingsOpen, setIsSettingsOpen] = useState(false);
    const [email, setEmail] = useState(user?.email || '');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState({ type: '', text: '' });
    const [isSaving, setIsSaving] = useState(false);

    useEffect(() => {
        if (user) {
            setEmail(user.email);
        }
    }, [user]);

    const handleSaveSettings = async (e) => {
        e.preventDefault();
        setIsSaving(true);
        setMessage({ type: '', text: '' });

        const payload = { email };
        if (password.trim()) {
            payload.password = password;
        }

        const res = await updateProfile(payload);
        setIsSaving(false);
        if (res.success) {
            setMessage({ type: 'success', text: 'Account updated successfully!' });
            setPassword('');
            setTimeout(() => {
                setIsSettingsOpen(false);
                setMessage({ type: '', text: '' });
            }, 1200);
        } else {
            setMessage({ type: 'error', text: res.error });
        }
    };
    
    let DashboardComponent;
    if (user?.role === 'hr_admin' || user?.role === 'system_admin') {
        DashboardComponent = HRDashboardPage;
    } else if (user?.role === 'manager') {
        DashboardComponent = TeamProgressPage;
    } else {
        DashboardComponent = EmployeeDashboardPage;
    }
    
    return (
        <div className="min-h-screen flex flex-col bg-slate-50">
            {/* Top Navigation */}
            <nav className="border-b border-slate-200 bg-white/80 backdrop-blur-md sticky top-0 z-50 shadow-sm">
                <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center shadow-sm">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
                        </div>
                        <span className="font-display font-bold text-slate-900 tracking-wide">NexusAI</span>
                    </div>
                    
                    <div className="flex items-center gap-4">
                        <div className="hidden md:flex items-center gap-3 text-sm font-medium">
                            <span className="text-slate-700">{user?.email || user?.username}</span>
                            <span className="px-2.5 py-1 rounded-md bg-indigo-50 text-indigo-700 border border-indigo-100 text-xs uppercase tracking-wider">{user?.role}</span>
                        </div>
                        
                        <div className="h-6 w-px bg-slate-200 hidden md:block"></div>
                        
                        <button 
                            onClick={() => setIsSettingsOpen(true)}
                            className="px-3 py-1.5 text-xs font-medium bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 rounded-lg transition-colors flex items-center gap-1.5 cursor-pointer shadow-sm"
                        >
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.38a2 2 0 0 0-.73-2.73l-.15-.1a2 2 0 0 1-1-1.72v-.51a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>
                            Settings
                        </button>

                        <button 
                            onClick={logout}
                            className="text-sm font-medium text-slate-500 hover:text-slate-900 transition-colors flex items-center gap-1.5"
                        >
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
                            Logout
                        </button>
                    </div>
                </div>
            </nav>

            {/* Settings Modal */}
            {isSettingsOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4 animate-fade-in">
                    <div className="glass-card w-full max-w-md p-6 relative bg-white border border-slate-200 shadow-xl rounded-2xl">
                        <div className="flex justify-between items-center mb-5 pb-3 border-b border-slate-100">
                            <h3 className="text-xl font-bold text-slate-900 flex items-center gap-2">
                                Account Settings
                            </h3>
                            <button 
                                onClick={() => setIsSettingsOpen(false)}
                                className="text-slate-400 hover:text-slate-700 transition-colors p-1"
                            >
                                ✕
                            </button>
                        </div>

                        {message.text && (
                            <div className={`p-3 rounded-lg text-sm mb-4 ${message.type === 'success' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-red-50 text-red-700 border border-red-200'}`}>
                                {message.text}
                            </div>
                        )}

                        <form onSubmit={handleSaveSettings} className="space-y-4">
                            <div>
                                <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-1">Email Address</label>
                                <input 
                                    type="email" 
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="w-full bg-white border border-slate-300 text-slate-900 rounded-lg p-2.5 text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-1">New Password (Optional)</label>
                                <input 
                                    type="password" 
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="Leave blank to keep current"
                                    className="w-full bg-white border border-slate-300 text-slate-900 rounded-lg p-2.5 text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                                />
                                <small className="text-slate-500 text-xs mt-1 block">Min 8 chars, uppercase, lowercase, digit, special char.</small>
                            </div>

                            <div className="flex justify-end gap-3 pt-3">
                                <button
                                    type="button"
                                    onClick={() => setIsSettingsOpen(false)}
                                    className="px-4 py-2 text-sm text-slate-600 hover:text-slate-900 transition-colors cursor-pointer"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    disabled={isSaving}
                                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium transition-colors cursor-pointer flex items-center gap-2 shadow-sm"
                                >
                                    {isSaving ? 'Saving...' : 'Save Changes'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Main Content Area */}
            <main className="flex-1 p-6 md:p-8 max-w-7xl mx-auto w-full">
                <DashboardComponent />
            </main>
        </div>
    );
};

function App() {
    return (
        <AuthProvider>
            <BrowserRouter>
                <Routes>
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/register" element={<RegisterPage />} />
                    <Route 
                        path="/*" 
                        element={
                            <ProtectedRoute>
                                <DashboardRouter />
                                <ChatWidget />
                            </ProtectedRoute>
                        } 
                    />
                </Routes>
            </BrowserRouter>
        </AuthProvider>
    );
}

export default App;
