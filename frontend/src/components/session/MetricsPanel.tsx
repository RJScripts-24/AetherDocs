import React, { useEffect, useState } from 'react';
import { BarChart, Activity, Zap, Layers, CheckCircle, Brain, Clock, FileText, Video } from 'lucide-react';
import { PALETTE } from '../../styles/palette';
import { API_CONFIG } from '../../api/config';

interface MetricsPanelProps {
    isDarkMode: boolean;
    sessionId?: string;
}

interface MetricsData {
    retrieval_accuracy: string;
    answer_quality: string;
    processing_stats: {
        transcription_segments: number;
        unique_insights: number;
        topic_coverage: Record<string, number>;
    };
    input_sources?: {
        files: string[];
        youtube_urls: string[];
    };
    comparison_text: string;
    ablation_text: string;
}

export function MetricsPanel({ isDarkMode, sessionId }: MetricsPanelProps) {
    const [metrics, setMetrics] = useState<MetricsData | null>(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!sessionId) return;

        let intervalId: ReturnType<typeof setInterval> | null = null;

        const fetchMetrics = async () => {
            setLoading(true);
            try {
                const response = await fetch(`${API_CONFIG.BASE_URL}/download/${sessionId}/metrics.json`);
                if (response.ok) {
                    const data = await response.json();
                    setMetrics(data);
                    // Stop polling once we have metrics
                    if (intervalId) {
                        clearInterval(intervalId);
                        intervalId = null;
                    }
                } else {
                    console.warn("Metrics not found (yet). Will retry...");
                }
            } catch (e) {
                console.error("Failed to fetch metrics", e);
            } finally {
                setLoading(false);
            }
        };

        // Fetch immediately, then poll every 5s until metrics arrive
        fetchMetrics();
        intervalId = setInterval(fetchMetrics, 5000);

        return () => {
            if (intervalId) clearInterval(intervalId);
        };
    }, [sessionId]);

    const cardStyle = {
        backgroundColor: isDarkMode ? 'rgba(44, 57, 48, 0.4)' : 'rgba(255, 255, 255, 0.6)',
        borderColor: isDarkMode ? 'rgba(162, 123, 92, 0.2)' : 'rgba(63, 79, 68, 0.15)',
        color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen
    };

    if (!metrics && loading) {
        return <div className="p-6 text-center opacity-70" style={{ color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen }}>Loading Session Metrics...</div>;
    }

    if (!metrics) {
        return (
            <div className="p-6 flex flex-col items-center justify-center h-full text-center opacity-60" style={{ color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen }}>
                <Activity size={48} className="mb-4 opacity-50" />
                <p>Processing Intelligence...</p>
                <span className="text-xs mt-2">Metrics will appear after pipeline completion.</span>
            </div>
        );
    }

    // Parse strings "92.4% ..." to numbers for visualization if needed
    const accuracyVal = parseFloat(metrics.retrieval_accuracy) || 0;
    const qualityVal = parseFloat(metrics.answer_quality.split('/')[0]) || 0;

    return (
        <div className="flex flex-col h-full gap-6 p-6 overflow-y-auto">
            {/* Header */}
            <div className="flex items-center gap-3 pb-4 border-b" style={{ borderColor: isDarkMode ? 'rgba(162, 123, 92, 0.15)' : 'rgba(63, 79, 68, 0.2)' }}>
                <Activity size={24} style={{ color: PALETTE.leather }} />
                <h2 className="text-xl font-medium" style={{ color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen }}>
                    Real-Time Efficiency Report
                </h2>
            </div>

            {/* 1. Evaluation Metrics */}
            <div className="space-y-4">
                <h3 className="text-sm font-semibold uppercase tracking-wider opacity-70" style={{ color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen }}>
                    1. Session Metrics (Dynamic)
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Confidence Score */}
                    <div className="p-4 rounded-lg border" style={cardStyle}>
                        <div className="flex justify-between items-center mb-2">
                            <span className="text-sm font-medium">Confidence Score</span>
                            <span className="text-xs px-2 py-0.5 rounded bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">Semantic Density</span>
                        </div>
                        <div className="flex items-end gap-2">
                            <span className="text-3xl font-bold">{metrics.retrieval_accuracy.split(' ')[0]}</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-1.5 mt-3 dark:bg-gray-700">
                            <div className="bg-blue-600 h-1.5 rounded-full" style={{ width: `${accuracyVal}%` }}></div>
                        </div>
                    </div>

                    {/* Quality Score */}
                    <div className="p-4 rounded-lg border" style={cardStyle}>
                        <div className="flex justify-between items-center mb-2">
                            <span className="text-sm font-medium">Global Quality</span>
                            <span className="text-xs px-2 py-0.5 rounded bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">AI Evaluation</span>
                        </div>
                        <div className="flex items-end gap-2">
                            <span className="text-3xl font-bold">{metrics.answer_quality.split(' ')[0]}</span>
                            <span className="text-sm pb-1 opacity-70">/ 5.0</span>
                        </div>
                        <div className="flex gap-1 mt-3">
                            {[1, 2, 3, 4, 5].map((star) => (
                                <div
                                    key={star}
                                    className="h-1.5 flex-1 rounded-full"
                                    style={{
                                        backgroundColor: star <= Math.round(qualityVal) ? PALETTE.success : (isDarkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)')
                                    }}
                                />
                            ))}
                        </div>
                    </div>
                </div>

                {/* Processing Stats */}
                <div className="grid grid-cols-2 gap-4">
                    <div className="p-3 rounded border flex items-center gap-3" style={cardStyle}>
                        <Clock size={18} className="opacity-60" />
                        <div>
                            <div className="text-xs opacity-70">Segments Processed</div>
                            <div className="font-bold">{metrics.processing_stats.transcription_segments}</div>
                        </div>
                    </div>
                    <div className="p-3 rounded border flex items-center gap-3" style={cardStyle}>
                        <Brain size={18} className="opacity-60" />
                        <div>
                            <div className="text-xs opacity-70">Unique Insights</div>
                            <div className="font-bold">{metrics.processing_stats.unique_insights}</div>
                        </div>
                    </div>
                </div>
            </div>

            {/* 2. Confusion Matrix / Topic Heatmap */}
            <div className="space-y-4">
                <h3 className="text-sm font-semibold uppercase tracking-wider opacity-70" style={{ color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen }}>
                    2. Content Distribution (Confusion Matrix Proxy)
                </h3>
                <div className="p-4 rounded-lg border" style={cardStyle}>
                    <p className="text-xs mb-3 opacity-80">Frequency of technical concepts detected in the synthesis layer.</p>
                    {metrics.processing_stats.topic_coverage && Object.keys(metrics.processing_stats.topic_coverage).length > 0 ? (
                        <div className="grid grid-cols-2 gap-2">
                            {Object.entries(metrics.processing_stats.topic_coverage).map(([topic, count]) => (
                                <div key={topic} className="flex justify-between items-center p-2 rounded" style={{
                                    backgroundColor: isDarkMode ? 'rgba(0,0,0,0.2)' : 'rgba(0,0,0,0.05)'
                                }}>
                                    <span className="text-sm font-medium">{topic}</span>
                                    <span className="text-xs font-mono bg-gray-500/20 px-1.5 py-0.5 rounded">{count}</span>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="text-sm italic opacity-50">No specific technical clusters identified.</p>
                    )}
                </div>
            </div>

            {/* 3. Comparison */}
            <div className="space-y-4">
                <h3 className="text-sm font-semibold uppercase tracking-wider opacity-70" style={{ color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen }}>
                    3. Comparison vs. Standard RAG
                </h3>
                <div className="p-5 rounded-lg border relative overflow-hidden" style={cardStyle}>
                    <div className="absolute top-0 right-0 p-4 opacity-5">
                        <Zap size={100} />
                    </div>
                    <div
                        className="text-sm leading-relaxed opacity-90"
                        dangerouslySetInnerHTML={{ __html: metrics.comparison_text }}
                    />
                </div>
            </div>

            {/* 4. Ablation Study */}
            <div className="space-y-4">
                <h3 className="text-sm font-semibold uppercase tracking-wider opacity-70" style={{ color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen }}>
                    4. Ablation Study
                </h3>
                <div className="p-4 rounded-lg border" style={cardStyle}>
                    <div
                        className="text-sm leading-relaxed opacity-90 space-y-2"
                        dangerouslySetInnerHTML={{ __html: metrics.ablation_text }}
                    />
                </div>
            </div>

            {/* 5. Source Documents */}
            {metrics.input_sources && (
                <div className="space-y-4">
                    <h3 className="text-sm font-semibold uppercase tracking-wider opacity-70" style={{ color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen }}>
                        5. Session Input Sources
                    </h3>
                    <div className="p-4 rounded-lg border space-y-3" style={cardStyle}>
                        {metrics.input_sources.files.length > 0 && (
                            <div>
                                <p className="text-xs font-semibold mb-2 opacity-70">Uploaded Documents</p>
                                {metrics.input_sources.files.map((file, idx) => (
                                    <div key={idx} className="flex items-center gap-2 p-2 rounded mb-1" style={{
                                        backgroundColor: isDarkMode ? 'rgba(0,0,0,0.2)' : 'rgba(0,0,0,0.05)'
                                    }}>
                                        <FileText size={14} className="opacity-60" />
                                        <span className="text-sm">{file}</span>
                                    </div>
                                ))}
                            </div>
                        )}
                        {metrics.input_sources.youtube_urls.length > 0 && (
                            <div>
                                <p className="text-xs font-semibold mb-2 opacity-70">YouTube Videos</p>
                                {metrics.input_sources.youtube_urls.map((url, idx) => (
                                    <div key={idx} className="flex items-center gap-2 p-2 rounded mb-1" style={{
                                        backgroundColor: isDarkMode ? 'rgba(0,0,0,0.2)' : 'rgba(0,0,0,0.05)'
                                    }}>
                                        <Video size={14} className="opacity-60" />
                                        <a href={url} target="_blank" rel="noopener noreferrer" className="text-sm underline truncate" style={{ color: PALETTE.leather }}>
                                            {url}
                                        </a>
                                    </div>
                                ))}
                            </div>
                        )}
                        {metrics.input_sources.files.length === 0 && metrics.input_sources.youtube_urls.length === 0 && (
                            <p className="text-sm italic opacity-50">No source documents recorded.</p>
                        )}
                    </div>
                </div>
            )}

            <div className="mt-auto pt-6 text-center">
                <p className="text-xs opacity-50 italic" style={{ color: isDarkMode ? PALETTE.beige : PALETTE.forestGreen }}>
                    Metrics generated in real-time based on session {sessionId?.slice(0, 8)}...
                </p>
            </div>
        </div>
    );
}
