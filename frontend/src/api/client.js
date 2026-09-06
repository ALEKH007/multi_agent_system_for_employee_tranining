import axios from 'axios';

// Get CSRF token from cookie if needed (Django sets it by default if configured)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const client = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
    withCredentials: true, // Crucial for sending cookies (JWT and CSRF)
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    },
});

// Request interceptor to attach CSRF token
client.interceptors.request.use((config) => {
    // Note: Do not store Auth tokens (JWT/Bearer) in localStorage.
    // We rely entirely on HttpOnly cookies as per secure coding guidelines.

    // Always enforce HTTPS in production
    if (import.meta.env.PROD && config.baseURL && config.baseURL.startsWith('http://')) {
        config.baseURL = config.baseURL.replace('http://', 'https://');
    }

    // Only attach CSRF for mutating state
    if (config.method && ['post', 'put', 'delete', 'patch'].includes(config.method.toLowerCase())) {
        const csrfToken = getCookie('csrftoken');
        if (csrfToken) {
            config.headers['X-CSRFToken'] = csrfToken;
        }
    }
    
    return config;
}, (error) => {
    return Promise.reject(error);
});

// Response interceptor to handle global errors (like 401 Unauthorized)
client.interceptors.response.use((response) => {
    return response;
}, (error) => {
    if (error.response && error.response.status === 401) {
        // Clear memory state if we have any, and redirect
        // We use window.location to force a full reload and clear any client-side cached data
        if (window.location.pathname !== '/login') {
            window.location.href = '/login';
        }
    }
    
    // Log errors securely (avoid printing full object to console in prod)
    if (import.meta.env.DEV) {
        console.error('API Error:', error.response?.status, error.message);
    }
    
    return Promise.reject(error);
});

export default client;
