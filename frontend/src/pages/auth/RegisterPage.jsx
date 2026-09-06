import React, { useState } from 'react';
import client from '../../api/client';
import { Mail, Lock, Shield, AlertCircle, Loader2, Eye, EyeOff } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const RegisterPage = () => {
    const [formData, setFormData] = useState({
        email: '',
        password: ''
    });
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [showPassword, setShowPassword] = useState(false);

    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setIsSubmitting(true);
        
        try {
            await client.post('/auth/register/', formData);
            setSuccess(true);
            setTimeout(() => {
                navigate('/login');
            }, 3000);
        } catch (err) {
            setError(err.response?.data?.detail || 'Registration failed. Please check inputs.');
        } finally {
            setIsSubmitting(false);
        }
    };

    if (success) {
        return (
            <div className="auth-container">
                <div className="glass-card auth-card animate-fade-in text-center">
                    <div className="success-icon-wrapper">
                        <Shield className="success-icon" />
                    </div>
                    <h2>Registration Successful</h2>
                    <p className="text-muted">Account created. Redirecting to login...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="auth-container">
            <div className="glass-card auth-card animate-fade-in">
                <div className="auth-header">
                    <h2>Create Employee Account</h2>
                    <p className="text-muted">HR links your account to an employee profile after verification.</p>
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
                                name="email" 
                                className="input-field with-icon" 
                                value={formData.email}
                                onChange={handleChange}
                                placeholder="john@company.com"
                                required 
                            />
                        </div>
                    </div>
                    
                    <div className="form-group">
                        <label>Temporary Password</label>
                        <div className="input-wrapper">
                            <Lock className="input-icon" />
                            <input 
                                type={showPassword ? 'text' : 'password'} 
                                name="password" 
                                className="input-field with-icon"
                                value={formData.password}
                                onChange={handleChange}
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
                        <small className="password-hint">Min 8 characters.</small>
                    </div>

                    <button 
                        type="submit" 
                        disabled={isSubmitting}
                        className="btn btn-primary submit-btn"
                    >
                        {isSubmitting ? <Loader2 className="spinner" /> : 'Create Account'}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default RegisterPage;
