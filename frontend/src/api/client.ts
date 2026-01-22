import {
    ChatRequest,
    ChatResponse,
    FileUploadMetadata,
    LocatorResponse,
    RevokeResponse,
    SessionResponse,
    SynthesisResponse,
    TriggerSynthesisRequest,
} from './types';

const BASE_URL = 'http://localhost:8000/api/v1';

export class AetherDocsClient {
    private static async request<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<T> {
        const response = await fetch(`${BASE_URL}${endpoint}`, {
            ...options,
            headers: {
                ...options.headers,
            },
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }

        return response.json();
    }

    static async startSession(): Promise<SessionResponse> {
        return this.request<SessionResponse>('/session/start', {
            method: 'POST',
        });
    }

    static async revokeSession(sessionId: string): Promise<RevokeResponse> {
        return this.request<RevokeResponse>(`/session/${sessionId}/revoke`, {
            method: 'POST',
        });
    }

    static async uploadFile(
        sessionId: string,
        file: File
    ): Promise<FileUploadMetadata> {
        const formData = new FormData();
        formData.append('session_id', sessionId);
        formData.append('file', file);

        // Note: Content-Type header is not set manually for FormData, 
        // fetch handles it automatically with the boundary.
        return this.request<FileUploadMetadata>('/upload/', {
            method: 'POST',
            body: formData,
        });
    }

    static async triggerSynthesis(
        request: TriggerSynthesisRequest
    ): Promise<SynthesisResponse> {
        return this.request<SynthesisResponse>('/upload/synthesize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(request),
        });
    }

    static async chatQuery(request: ChatRequest): Promise<ChatResponse> {
        return this.request<ChatResponse>('/chat/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(request),
        });
    }

    static async chatLocator(request: ChatRequest): Promise<LocatorResponse> {
        return this.request<LocatorResponse>('/chat/locator', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(request),
        });
    }
}
