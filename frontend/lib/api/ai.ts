import { apiGet, apiPost } from './client';
import {
  AIRecommendationResponse,
  AIChatRequest,
  AIChatResponse,
  AIChatMessage,
  SubscriptionAuditResponse,
  Budget50_30_20,
} from '../../types/ai';

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

/**
 * Ask ExpenseFlow AI conversational assistant (Step 5 Structured RAG).
 */
export async function chatWithAI(
  message: string,
  conversationHistory: AIChatMessage[] = []
): Promise<AIChatResponse> {
  return apiPost<AIChatResponse, AIChatRequest>('/ai/chat', {
    message,
    conversation_history: conversationHistory,
  });
}

/**
 * Get recurring subscriptions and fixed commitment audit (Step 3).
 */
export async function getSubscriptionAudit(): Promise<SubscriptionAuditResponse> {
  return apiGet<SubscriptionAuditResponse>('/ai/subscriptions');
}

/**
 * Get 50/30/20 budget framework analysis and rebalancing advice (Step 4).
 */
export async function get50_30_20Breakdown(): Promise<Budget50_30_20> {
  return apiGet<Budget50_30_20>('/ai/50-30-20');
}
