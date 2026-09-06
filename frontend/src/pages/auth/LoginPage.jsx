import React, { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useNavigate } from 'react-router-dom';
import { Mail, Lock, AlertCircle, Loader2, Eye, EyeOff } from 'lucide-react';

const LoginPage = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setIsSubmitting(true);
        
        if (!email || !password) {
            setError('Please fill in all fields.');
            setIsSubmitting(false);
            return;
        }

        const result = await login(email, password);
        
        if (result.success) {
            navigate('/');
        } else {
            setError(result.error);
            setIsSubmitting(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="glass-card auth-card animate-fade-in has-bg-blobs">
                <div className="blob blob-1"></div>
                <div className="blob blob-2"></div>
                
                <div className="auth-header">
                    <h2>Welcome Back</h2>
                    <p className="text-muted">Sign in to access your training dashboard</p>
                </div>
                
                {error && (
                    <div className="alert-error">
                        <AlertCircle className="alert-icon" />
                        <span>{error}</span>
                    </div>
                )}
                
                <form onSubmit={handleSubmit} className="auth-form">
                    <div className="form-group">
                        <label>Email Address</label>
                        <div className="input-wrapper">
                            <Mail className="input-icon" />
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="input-field with-icon"
                                placeholder="you@company.com"
                                required
                            />
                        </div>
                    </div>
                    
                    <div className="form-group">
                        <label>Password</label>
                        <div className="input-wrapper">
                            <Lock className="input-icon" />
                            <input
                                type={showPassword ? 'text' : 'password'}
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="input-field with-icon"
                                placeholder="••••••••"
                                required
                            />
                            <button
                                type="button"
                                onClick={() => setShowPassword(!showPassword)}
                                className="password-toggle-btn"
                                aria-label={showPassword ? 'Hide password' : 'Show password'}
                            >
                                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                            </button>
                        </div>
                    </div>
                    
                    <button
                        type="submit"
                        disabled={isSubmitting}
                        className="btn btn-primary submit-btn"
                    >
                        {isSubmitting ? <Loader2 className="spinner" /> : 'Sign In'}
                    </button>
                </form>

                {/* Quick Demo Login Bar */}
                <div className="mt-6 pt-6 border-t border-slate-800 text-center">
                    <p className="text-xs text-slate-400 mb-3 uppercase tracking-wider font-semibold">Quick Demo Login</p>
                    <div className="grid grid-cols-3 gap-2">
                        <button
                            type="button"
                            onClick={() => { setEmail('hr@company.com'); setPassword('Admin@12345'); }}
                            className="px-2 py-1.5 rounded-lg bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 text-xs font-medium transition-colors"
                        >
                            HR Admin
                        </button>
                        <button
                            type="button"
                            onClick={() => { setEmail('manager@company.com'); setPassword('Admin@12345'); }}
                            className="px-2 py-1.5 rounded-lg bg-purple-500/10 hover:bg-purple-500/20 text-purple-400 border border-purple-500/30 text-xs font-medium transition-colors"
                        >
                            Manager
                        </button>
                        <button
                            type="button"
                            onClick={() => { setEmail('employee@company.com'); setPassword('Admin@12345'); }}
                            className="px-2 py-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-medium transition-colors"
                        >
                            Employee
                        </button>
                    </div>
                </div>

                <div className="mt-4 text-center">
                    <button
                        type="button"
                        onClick={() => navigate('/register')}
                        className="text-sm text-slate-400 hover:text-indigo-400 transition-colors font-medium cursor-pointer"
                    >
                        Need a custom account? <span className="text-indigo-400 underline">Register here</span>
                    </button>
                </div>
            </div>
        </div>
    );
};

export default LoginPage;

