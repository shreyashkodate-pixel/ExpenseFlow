import { apiGet, apiPost } from './client';
import { AIRecommendationResponse } from '../../types/ai';

/**
 * Fetch cached or fresh AI spending insights and recommendations for the current user.
 */
export async function getAIRecommendations(): Promise<AIRecommendationResponse> {
  return apiGet<AIRecommendationResponse>('/ai/recommendations');
}

/**
 * Force clear cache and generate fresh AI insights (rate-limited to 5 req/min).
 */
export async function refreshAIRecommendations(): Promise<AIRecommendationResponse> {
  return apiPost<AIRecommendationResponse, Record<string, never>>('/ai/recommendations/refresh', {});
}
