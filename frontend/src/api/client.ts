
import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000/api';

// Create Axios Instance
const client = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request Interceptor to add Token
client.interceptors.request.use((config) => {
    const token = sessionStorage.getItem('auth_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export const api = {
    login: async (pan: string, password: string) => {
        // Backend expects form-data for OAuth2PasswordRequestForm
        const formData = new FormData();
        formData.append('username', pan);
        formData.append('password', password);

        // BUT our backend code also accepts JSON if we didn't use OAuth2PasswordRequestForm strictly?
        // Actually, OAuth2PasswordRequestForm requires form-data.
        // Let's check auth.py: `form_data: OAuth2PasswordRequestForm = Depends()`
        // So we MUST send form data.

        const response = await client.post('/auth/login', formData, {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        });
        return response.data;
    },

    getDashboard: async () => {
        const response = await client.get('/dashboard');
        return response.data;
    },

    register: async (userData: any) => {
        const response = await client.post('/auth/register', userData);
        return response.data;
    },

    getProfile: async () => {
        const response = await client.get('/profile');
        return response.data;
    },
    getReturnHistory: async () => {
        const response = await client.get("/returns");
        return response.data;
    },
    getNoticeHistory: async () => {
        const response = await client.get("/notices");
        return response.data;
    },
    triggerSync: async (password: string) => {
        const response = await client.post("/sync/itr", { password });
        return response.data;
    },
};

export default api;
