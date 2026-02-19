
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
    login: async (pan: string, password: string, questionnaireData?: any) => {
        // Backend expects form-data for OAuth2PasswordRequestForm
        // We use URLSearchParams to ensure application/x-www-form-urlencoded header is set correctly
        const params = new URLSearchParams();
        params.append('username', pan);
        params.append('password', password);

        if (questionnaireData) {
            params.append('questionnaire_data', JSON.stringify(questionnaireData));
        }

        const response = await client.post('/auth/login', params, {
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

    // Sync APIs
    triggerAllSync: async (password: string) => {
        const response = await client.post("/sync/all", { password });
        return response.data;
    },
    triggerSync: async (password: string) => {
        // Default to ITR for backward compatibility or general sync
        const response = await client.post("/sync/itr", { password });
        return response.data;
    },
    triggerITRSync: async (password: string) => {
        const response = await client.post("/sync/itr", { password });
        return response.data;
    },
    triggerAISSync: async (password: string) => {
        const response = await client.post("/sync/ais", { password });
        return response.data;
    },
    trigger26ASSync: async (password: string) => {
        const response = await client.post("/sync/26as", { password });
        return response.data;
    },
    triggerNoticesSync: async (password: string) => {
        const response = await client.post("/sync/eproceedings", { password });
        return response.data;
    },
    verifyCredentials: async (password: string) => {
        const response = await client.post("/sync/verify", { password });
        return response.data;
    },

    getSyncStatus: async () => {
        const response = await client.get("/sync/status");
        return response.data;
    },

    updateProfileQuestionnaire: async (data: any) => {
        const response = await client.put("/profile/questionnaire", { items: data });
        return response.data;
    },

    deleteAccount: async () => {
        const response = await client.delete("/profile/me");
        return response.data;
    },
};

export default api;
