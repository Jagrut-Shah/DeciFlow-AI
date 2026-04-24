const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

const generateTraceId = () => Math.random().toString(36).substring(2, 15);

async function fetchWithRetry(url: string, options: RequestInit, retries = 2): Promise<Response> {
    try {
        const response = await fetch(url, options);
        if (response.status === 503 && retries > 0) {
            await new Promise(resolve => setTimeout(resolve, 1000));
            return fetchWithRetry(url, options, retries - 1);
        }
        return response;
    } catch (error) {
        if (retries > 0) {
            await new Promise(resolve => setTimeout(resolve, 1000));
            return fetchWithRetry(url, options, retries - 1);
        }
        throw error;
    }
}

export const apiClient = {
    async post(endpoint: string, data: any) {
        const traceId = generateTraceId();
        const response = await fetchWithRetry(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Trace-ID': traceId,
            },
            body: JSON.stringify(data),
        });
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.message || 'API Request Failed');
        }
        
        return response.json();
    },
    
    async get(endpoint: string) {
        const traceId = generateTraceId();
        const response = await fetchWithRetry(`${API_BASE_URL}${endpoint}`, {
            headers: {
                'X-Trace-ID': traceId,
            }
        });
        if (!response.ok) throw new Error('API Request Failed');
        return response.json();
    }
};

