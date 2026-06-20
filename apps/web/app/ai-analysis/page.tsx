"use client";

import { useState } from "react";
import { GlassCard } from "@/components/ui/glass-card";
import { apiClient } from "@/lib/api-client";
import { motion } from "framer-motion";

export default function AIAnalysisPage() {
  const [symbol, setSymbol] = useState("BTCUSDT");
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState<any>(null);

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      const data = await apiClient.getAISignal(symbol);
      setAnalysis(data);
    } catch (error) {
      console.error("Analysis error:", error);
      alert("Failed to generate analysis. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-white">AI Analysis</h1>
          <p className="text-muted-foreground mt-1">Generate detailed trading signals with AI</p>
        </div>

        {/* Input */}
        <GlassCard>
          <div className="flex gap-4">
            <input
              type="text"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              placeholder="e.g., BTCUSDT"
              className="flex-1 px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-muted-foreground focus:outline-none focus:border-primary/50"
            />
            <button
              onClick={handleAnalyze}
              disabled={loading}
              className="px-6 py-3 rounded-xl bg-primary hover:bg-primary/90 text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {loading ? "Analyzing..." : "Generate Signal"}
            </button>
          </div>
        </GlassCard>

        {/* Results */}
        {analysis && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <GlassCard>
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-white">{analysis.symbol}</h2>
                  <p className="text-muted-foreground">{new Date(analysis.timestamp).toLocaleString()}</p>
                </div>
                <div className={`px-4 py-2 rounded-xl text-lg font-bold ${
                  analysis.direction === 'LONG' ? 'bg-accent/20 text-accent' :
                  analysis.direction === 'SHORT' ? 'bg-destructive/20 text-destructive' :
                  'bg-muted text-muted-foreground'
                }`}>
                  {analysis.direction}
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="p-4 rounded-xl bg-white/5">
                  <p className="text-sm text-muted-foreground">Confidence</p>
                  <p className="text-2xl font-bold text-white mt-1">{analysis.confidence_score}%</p>
                </div>
                <div className="p-4 rounded-xl bg-white/5">
                  <p className="text-sm text-muted-foreground">Risk/Reward</p>
                  <p className="text-2xl font-bold text-white mt-1">{analysis.risk_reward_ratio}</p>
                </div>
                <div className="p-4 rounded-xl bg-white/5">
                  <p className="text-sm text-muted-foreground">Risk Level</p>
                  <p className="text-lg font-semibold text-white mt-1">{analysis.risk_classification}</p>
                </div>
                <div className="p-4 rounded-xl bg-white/5">
                  <p className="text-sm text-muted-foreground">Timeframe</p>
                  <p className="text-lg font-semibold text-white mt-1">{analysis.timeframe || "4h-1d"}</p>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-semibold text-white mb-2">Entry Zone</h3>
                  <p className="text-muted-foreground">
                    ${analysis.entry_zone?.min?.toLocaleString()} - ${analysis.entry_zone?.max?.toLocaleString()}
                  </p>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white mb-2">Stop Loss</h3>
                  <p className="text-destructive">${analysis.stop_loss?.toLocaleString()}</p>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white mb-2">Take Profit Targets</h3>
                  <div className="flex gap-3">
                    {analysis.take_profit_targets?.map((tp: number, i: number) => (
                      <div key={i} className="px-4 py-2 rounded-lg bg-accent/10 text-accent">
                        TP{i + 1}: ${tp.toLocaleString()}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </GlassCard>

            <GlassCard>
              <h3 className="text-lg font-semibold text-white mb-3">AI Reasoning</h3>
              <p className="text-muted-foreground leading-relaxed">{analysis.reasoning}</p>
            </GlassCard>

            <GlassCard>
              <h3 className="text-lg font-semibold text-white mb-3">Market Outlook</h3>
              <p className="text-muted-foreground leading-relaxed">{analysis.market_outlook}</p>
            </GlassCard>

            {analysis.disclaimer && (
              <div className="p-4 rounded-xl bg-destructive/10 border border-destructive/20">
                <p className="text-sm text-destructive">{analysis.disclaimer}</p>
              </div>
            )}
          </motion.div>
        )}
      </div>
    </div>
  );
}
