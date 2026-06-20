const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const response = await fetch(url, {
      ...options,
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'An unknown error occurred' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async getMarketIndicators(symbol: string, interval: string = "60") {
    return this.request(`/api/v1/market/${symbol}/indicators?interval=${interval}`);
  }

  async getAISignal(symbol: string) {
    return this.request(`/api/v1/ai/analyze/${symbol}`, { method: 'POST' });
  }

  async getRecentSignals(limit: number = 20) {
    return this.request(`/api/v1/ai-signals/recent?limit=${limit}`);
  }

  async createPaperTrade(tradeData: any) {
    return this.request('/api/v1/paper-trades', {
      method: 'POST',
      body: JSON.stringify(tradeData),
    });
  }

  async getUserPaperTrades(userId: string) {
    return this.request(`/api/v1/paper-trades/${userId}`);
  }
}

export const apiClient = new ApiClient();
export { WS_BASE_URL };
