import { GlassCard } from "@/components/ui/glass-card";
import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 bg-gradient-to-br from-background via-background to-primary/5">
      <div className="max-w-4xl w-full space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20">
            <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
            <span className="text-sm font-medium text-primary">AI-Powered Trading Copilot</span>
          </div>
          <h1 className="text-5xl md:text-7xl font-bold bg-gradient-to-r from-white via-primary to-accent bg-clip-text text-transparent">
            HiveMind
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Advanced crypto market intelligence with real-time AI analysis, 
            risk management, and paper trading.
          </p>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
          <GlassCard delay={0.1} className="text-center">
            <div className="w-12 h-12 mx-auto mb-4 rounded-xl bg-primary/20 flex items-center justify-center">
              <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold mb-2">Real-Time AI Analysis</h3>
            <p className="text-sm text-muted-foreground">
              Advanced technical indicators and market sentiment analyzed by Groq AI
            </p>
          </GlassCard>

          <GlassCard delay={0.2} className="text-center">
            <div className="w-12 h-12 mx-auto mb-4 rounded-xl bg-accent/20 flex items-center justify-center">
              <svg className="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold mb-2">Risk Management</h3>
            <p className="text-sm text-muted-foreground">
              Automated position sizing and risk-reward calculations
            </p>
          </GlassCard>

          <GlassCard delay={0.3} className="text-center">
            <div className="w-12 h-12 mx-auto mb-4 rounded-xl bg-purple-500/20 flex items-center justify-center">
              <svg className="w-6 h-6 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold mb-2">Paper Trading</h3>
            <p className="text-sm text-muted-foreground">
              Practice strategies risk-free with virtual capital
            </p>
          </GlassCard>
        </div>

        {/* CTA */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center mt-12">
          <Link
            href="/dashboard"
            className="px-8 py-4 rounded-xl bg-primary hover:bg-primary/90 text-white font-semibold transition-all duration-300 shadow-lg shadow-primary/25"
          >
            Launch Dashboard
          </Link>
          <Link
            href="/ai-analysis"
            className="px-8 py-4 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-white font-semibold transition-all duration-300"
          >
            View AI Analysis
          </Link>
        </div>

        {/* Disclaimer */}
        <p className="text-xs text-muted-foreground text-center mt-12 max-w-xl mx-auto">
          ⚠️ This is a trading copilot for educational purposes only. 
          Not financial advice. Never trade with money you cannot afford to lose.
        </p>
      </div>
    </div>
  );
}
