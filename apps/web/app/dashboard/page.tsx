"use client";

import { useEffect, useState } from "react";
import { GlassCard } from "@/components/ui/glass-card";
import { apiClient, WS_BASE_URL } from "@/lib/api-client";
import { motion } from "framer-motion";

export default function DashboardPage() {
  const [recentSignals, setRecentSignals] = useState<any[]>([]);
  const [wsConnected, setWsConnected] = useState(false);

  useEffect(() => {
    // Fetch recent signals
    const fetchSignals = async () => {
      try {
        const data = await apiClient.getRecentSignals(10);
        setRecentSignals(data.signals || []);
      } catch (error) {
        console.error("Error fetching signals:", error);
      }
    };

    fetchSignals();

    // WebSocket connection
    const ws = new WebSocket(WS_BASE_URL + "/ws/signals");
    
    ws.onopen = () => {
      console.log("WebSocket connected");
      setWsConnected(true);
    };

    ws.onmessage = (event) => {
      const signal = JSON.parse(event.data);
      setRecentSignals(prev => [signal, ...prev].slice(0, 10));
    };

    ws.onclose = () => {
      setWsConnected(false);
    };

    return () => {
      ws.close();
    };
  }, []);

  return (
    <div className="min-h-screen p-6 animate-fade-in">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-white">Command Center</h1>
            <p className="text-muted-foreground mt-1">Real-time AI market intelligence</p>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-accent/10 border border-accent/20">
            <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-accent animate-pulse' : 'bg-destructive'}`} />
            <span className="text-xs font-medium text-accent">
              {wsConnected ? 'Live' : 'Disconnected'}
            </span>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <GlassCard delay={0.1}>
            <p className="text-sm text-muted-foreground">AI Win Rate (30d)</p>
            <p className="text-2xl font-bold text-white mt-1">78.4%</p>
            <p className="text-xs text-accent mt-1">+2.1% from last month</p>
          </GlassCard>
          <GlassCard delay={0.2}>
            <p className="text-sm text-muted-foreground">Active Signals</p>
            <p className="text-2xl font-bold text-white mt-1">{recentSignals.length}</p>
            <p className="text-xs text-primary mt-1">Real-time updates</p>
          </GlassCard>
          <GlassCard delay={0.3}>
            <p className="text-sm text-muted-foreground">Paper PnL</p>
            <p className="text-2xl font-bold text-accent mt-1">+$2,340</p>
            <p className="text-xs text-muted-foreground mt-1">Initial: $10,000</p>
          </GlassCard>
          <GlassCard delay={0.4}>
            <p className="text-sm text-muted-foreground">Fear & Greed</p>
            <p className="text-2xl font-bold text-white mt-1">62</p>
            <p className="text-xs text-accent mt-1">Greed</p>
          </GlassCard>
        </div>

        {/* Recent Signals */}
        <GlassCard delay={0.5} className="min-h-[400px]">
          <h3 className="text-lg font-semibold text-white mb-4">Live AI Signals</h3>
          <div className="space-y-3">
            {recentSignals.length === 0 ? (
              <p className="text-muted-foreground text-center py-8">No signals yet. Generate one in AI Analysis.</p>
            ) : (
              recentSignals.map((signal, index) => (
                <motion.div
                  key={signal.id || index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="p-4 rounded-xl bg-white/5 border border-white/10 flex items-center justify-between"
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-white">{signal.symbol}</span>
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                        signal.direction === 'LONG' ? 'bg-accent/20 text-accent' :
                        signal.direction === 'SHORT' ? 'bg-destructive/20 text-destructive' :
                        'bg-muted text-muted-foreground'
                      }`}>
                        {signal.direction}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">
                      Confidence: {signal.confidence_score}%
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-muted-foreground">
                      {new Date(signal.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                </motion.div>
              ))
            )}
          </div>
        </GlassCard>
      </div>
    </div>
  );
}
