import React, { createContext, useState, useEffect } from 'react';
import client from '../api/client';

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchUser = async () => {
            try {
                // The browser will automatically send the HttpOnly JWT cookie if it exists
                const response = await client.get('/auth/me/');
                setUser(response.data);
            } catch (error) {
                // Not authenticated or token expired
                setUser(null);
            } finally {
                setLoading(false);
            }
        };

        fetchUser();
    }, []);

    const login = async (email, password) => {
        try {
            const response = await client.post('/auth/login/', { email, password });
            setUser(response.data.user);
            return { success: true };
        } catch (error) {
            console.error('Login request error:', error);
            const serverMessage = error.response?.data?.detail 
                || error.response?.data?.error 
                || (Array.isArray(error.response?.data?.email) ? error.response.data.email[0] : null)
                || (Array.isArray(error.response?.data?.password) ? error.response.data.password[0] : null);
            
            return {
                success: false,
                error: serverMessage || (error.response ? 'Invalid email or password.' : 'Cannot connect to backend server. Please check connection.')
            };
        }
    };

    const logout = async () => {
        try {
            await client.post('/auth/logout/');
        } catch (error) {
            console.error('Logout failed on backend:', error);
        } finally {
            // Clear memory state and force full page reload to clear cache
            setUser(null);
            window.location.href = '/login';
        }
    };

    const updateProfile = async ({ email, password }) => {
        try {
            const response = await client.put('/auth/me/', { email, password });
            setUser(response.data.user);
            return { success: true, message: response.data.detail };
        } catch (error) {
            console.error('Update profile error:', error);
            const serverMessage = error.response?.data?.detail 
                || error.response?.data?.error;
            return {
                success: false,
                error: serverMessage || 'Failed to update account settings.'
            };
        }
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, logout, updateProfile }}>
            {children}
        </AuthContext.Provider>
    );
};
