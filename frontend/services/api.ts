// Ensure environment variable exists
if (!process.env.NEXT_PUBLIC_API_URL) {
  throw new Error("NEXT_PUBLIC_API_URL is not defined");
}

// ✅ Include /api/v1 prefix (VERY IMPORTANT)
const baseUrl = process.env.NEXT_PUBLIC_API_URL as string;

export const API_BASE_URL = `${baseUrl}/api/v1`;

// Generate trace ID (for debugging/logging)
const generateTraceId = () =>
  Math.random().toString(36).substring(2, 15);

// Retry wrapper for fetch (handles temporary failures)
async function fetchWithRetry(
  url: string,
  options: RequestInit,
  retries = 2
): Promise<Response> {
  try {
    const response = await fetch(url, options);

    // Retry on temporary server error
    if (response.status === 503 && retries > 0) {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      return fetchWithRetry(url, options, retries - 1);
    }

    return response;
  } catch (error) {
    if (retries > 0) {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      return fetchWithRetry(url, options, retries - 1);
    }
    throw error;
  }
}

// Main API client
export const apiClient = {
  async post(endpoint: string, data: any) {
    const traceId = generateTraceId();

    const response = await fetchWithRetry(`${API_BASE_URL}${endpoint}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Trace-ID": traceId,
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.message || "API Request Failed");
    }

    return response.json();
  },

  async get(endpoint: string) {
    const traceId = generateTraceId();

    const response = await fetchWithRetry(`${API_BASE_URL}${endpoint}`, {
      method: "GET",
      headers: {
        "X-Trace-ID": traceId,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.message || "API Request Failed");
    }

    return response.json();
  },
};
