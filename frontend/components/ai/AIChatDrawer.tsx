'use client';

import React, { useState, useRef, useEffect } from 'react';
import {
  MessageSquare,
  X,
  Send,
  Sparkles,
  Bot,
  User,
  RotateCcw,
  TrendingDown,
  PieChart,
  Flame,
  Lightbulb,
} from 'lucide-react';
import { AIChatMessage } from '../../types/ai';
import { chatWithAI } from '../../lib/api/ai';

interface ChatBubble {
  role: 'user' | 'assistant';
  content: string;
  followups?: string[];
  dataPoints?: string[];
}

const STARTER_PROMPTS = [
  { icon: <PieChart className="h-3 w-3" />, text: 'Where did most of my money go this month?' },
  { icon: <Flame className="h-3 w-3" />, text: 'Check my current budget pacing and burn rate' },
  { icon: <Lightbulb className="h-3 w-3" />, text: 'How can I save ₹3,000 more this month?' },
  { icon: <TrendingDown className="h-3 w-3" />, text: 'Audit my recurring subscriptions' },
];

export function AIChatDrawer() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatBubble[]>([
    {
      role: 'assistant',
      content:
        'Hi there! I am your **ExpenseFlow AI Assistant**. I have real-time access to your logged expenses, categories, and budgets.\n\nAsk me anything about your finances or pick one of the questions below!',
      followups: [
        'Where did most of my money go this month?',
        'Check my current budget pacing and burn rate',
        'How can I save ₹3,000 more this month?',
      ],
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const handleSend = async (textToSend?: string) => {
    const userMessage = (textToSend || input).trim();
    if (!userMessage || loading) return;

    setInput('');
    const newMessages: ChatBubble[] = [...messages, { role: 'user', content: userMessage }];
    setMessages(newMessages);
    setLoading(true);

    try {
      const history: AIChatMessage[] = newMessages
        .filter((m) => m.role === 'user' || m.role === 'assistant')
        .slice(-4)
        .map((m) => ({ role: m.role, content: m.content }));

      const res = await chatWithAI(userMessage, history);

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: res.reply,
          followups: res.suggested_followups,
          dataPoints: res.data_points_referenced,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content:
            'Sorry, I encountered an issue connecting to the AI engine. Please ensure your internet is active and try again.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      {/* Floating Trigger Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-40 flex items-center gap-2.5 rounded-full bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 px-4 py-3 text-white shadow-2xl shadow-indigo-500/40 transition-all duration-300 hover:scale-105 hover:shadow-indigo-500/60 focus:outline-none"
          title="Ask ExpenseFlow AI"
        >
          <Sparkles className="h-5 w-5 animate-spin-slow" />
          <span className="font-semibold text-sm tracking-wide">Ask AI</span>
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
          </span>
        </button>
      )}

      {/* Slide-out Drawer Overlay */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex justify-end bg-black/40 backdrop-blur-sm transition-opacity">
          <div className="relative flex h-full w-full max-w-md flex-col bg-white dark:bg-gray-950 border-l border-gray-200 dark:border-gray-800 shadow-2xl animate-slide-left">
            {/* Header */}
            <div className="flex items-center justify-between border-b border-gray-200 dark:border-gray-800 px-5 py-4 bg-gray-50/80 dark:bg-gray-900/60 backdrop-blur">
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 text-white shadow-md">
                  <Bot className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="font-semibold text-sm text-gray-900 dark:text-white">
                    ExpenseFlow AI Assistant
                  </h3>
                  <span className="text-2xs text-emerald-600 dark:text-emerald-400 flex items-center gap-1 font-medium">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-500"></span> Live Financial Ground Truth
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-1">
                <button
                  onClick={() =>
                    setMessages([
                      {
                        role: 'assistant',
                        content:
                          'Conversation reset. Ask me anything about your expenses, budgets, or savings goals!',
                      },
                    ])
                  }
                  className="rounded-lg p-1.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
                  title="Reset conversation"
                >
                  <RotateCcw className="h-4 w-4" />
                </button>
                <button
                  onClick={() => setIsOpen(false)}
                  className="rounded-lg p-1.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
                  title="Close Assistant"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            </div>

            {/* Messages Container */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((m, idx) => (
                <div
                  key={idx}
                  className={`flex gap-2.5 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {m.role === 'assistant' && (
                    <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-indigo-600/10 text-indigo-600 dark:text-indigo-400 mt-0.5">
                      <Bot className="h-4 w-4" />
                    </div>
                  )}

                  <div
                    className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-xs leading-relaxed ${
                      m.role === 'user'
                        ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-md'
                        : 'bg-gray-100 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 text-gray-800 dark:text-gray-200'
                    }`}
                  >
                    <div className="whitespace-pre-wrap">{m.content}</div>

                    {/* Data Points Referenced */}
                    {m.dataPoints && m.dataPoints.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-gray-200/40 dark:border-gray-800 flex flex-wrap gap-1">
                        {m.dataPoints.map((dp, dpIdx) => (
                          <span
                            key={dpIdx}
                            className="inline-block rounded px-1.5 py-0.5 text-3xs font-mono bg-indigo-500/10 text-indigo-500 dark:text-indigo-400"
                          >
                            {dp}
                          </span>
                        ))}
                      </div>
                    )}

                    {/* Follow-up Suggestion Chips */}
                    {m.followups && m.followups.length > 0 && (
                      <div className="mt-3 pt-2.5 border-t border-gray-200/40 dark:border-gray-800 space-y-1.5">
                        <span className="block text-3xs font-semibold uppercase tracking-wider text-gray-400 dark:text-gray-500">
                          Suggested Questions:
                        </span>
                        <div className="flex flex-col gap-1">
                          {m.followups.map((fu, fuIdx) => (
                            <button
                              key={fuIdx}
                              onClick={() => handleSend(fu)}
                              className="text-left text-2xs text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 transition-colors py-0.5"
                            >
                              👉 {fu}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {m.role === 'user' && (
                    <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-300 mt-0.5">
                      <User className="h-4 w-4" />
                    </div>
                  )}
                </div>
              ))}

              {/* Typing Indicator */}
              {loading && (
                <div className="flex gap-2.5 justify-start">
                  <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-indigo-600/10 text-indigo-600 dark:text-indigo-400">
                    <Bot className="h-4 w-4 animate-pulse" />
                  </div>
                  <div className="rounded-2xl bg-gray-100 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 px-4 py-3 flex items-center gap-1.5">
                    <span className="h-1.5 w-1.5 rounded-full bg-indigo-500 animate-bounce"></span>
                    <span
                      className="h-1.5 w-1.5 rounded-full bg-indigo-500 animate-bounce"
                      style={{ animationDelay: '0.15s' }}
                    ></span>
                    <span
                      className="h-1.5 w-1.5 rounded-full bg-indigo-500 animate-bounce"
                      style={{ animationDelay: '0.3s' }}
                    ></span>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Quick Starter Chips (when few messages) */}
            {messages.length <= 2 && (
              <div className="px-4 py-2 border-t border-gray-100 dark:border-gray-900 flex flex-wrap gap-1.5 bg-gray-50/50 dark:bg-gray-950">
                {STARTER_PROMPTS.map((sp, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSend(sp.text)}
                    className="flex items-center gap-1.5 rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 px-2.5 py-1 text-2xs text-gray-700 dark:text-gray-300 hover:border-indigo-500/50 transition-colors"
                  >
                    {sp.icon}
                    <span>{sp.text}</span>
                  </button>
                ))}
              </div>
            )}

            {/* Input Box */}
            <div className="p-3 border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950">
              <div className="relative flex items-center rounded-xl border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 focus-within:border-indigo-500 focus-within:ring-1 focus-within:ring-indigo-500 transition-all">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask a question about your spending..."
                  rows={1}
                  className="w-full resize-none bg-transparent px-3.5 py-2.5 text-xs text-gray-900 dark:text-gray-100 placeholder-gray-400 focus:outline-none max-h-24"
                />
                <button
                  onClick={() => handleSend()}
                  disabled={!input.trim() || loading}
                  className="mr-2 rounded-lg bg-indigo-600 p-2 text-white transition-all hover:bg-indigo-700 disabled:opacity-40 disabled:hover:bg-indigo-600"
                >
                  <Send className="h-3.5 w-3.5" />
                </button>
              </div>
              <p className="mt-1.5 text-center text-3xs text-gray-400">
                Answers grounded in your private financial records. No personal data shared.
              </p>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
