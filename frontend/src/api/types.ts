export interface SessionResponse {
    session_id: string;
    status: string;
}

export interface RevokeResponse {
    message: string;
    status: string;
}

export interface FileUploadMetadata {
    file_id: string;
    filename: string;
    file_size_mb: number;
    source_type: 'pdf' | 'docx' | 'pptx' | 'video' | 'audio' | 'image' | 'youtube';
}

export interface TriggerSynthesisRequest {
    session_id: string;
    mode?: 'fast' | 'deep';
    youtube_urls?: string[];
}

export interface SynthesisResponse {
    message: string;
    status: string;
}

export interface ChatRequest {
    session_id: string;
    query: string;
    history?: {
        role: string;
        content: string;
    }[];
}

export interface Citation {
    source_file: string;
    page_number?: number | null;
    timestamp?: string | null;
    snippet: string;
    score: number;
}

export interface ChatResponse {
    answer: string;
    citations: Citation[];
}

export interface LocatorMention {
    source: string;
    snippet: string;
    timestamp?: string | null;
    page?: number | null;
    score: number;
}

export interface LocatorResponse {
    mentions: LocatorMention[];
}

export interface StatusResponse {
    status: string;
    progress_percentage: number;
    current_step: string;
    error_message: string;
    result_pdf_url?: string;
}
