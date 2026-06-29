import { useEffect, useState } from 'react';
import { MetricCard } from '../components/ui/MetricCard';

interface LatestPriceData {
  symbol: string;
  close: number;
  trade_date: string;
  volume: number;
}

const otherMetrics = [
  { label: 'Active Models', value: '0', detail: 'Training not configured' },
  { label: 'Signals Today', value: '0', detail: 'Inference disabled' },
  { label: 'Backtests', value: '0', detail: 'Engine scaffolded' },
];

export function DashboardPage() {
  const [marketData, setMarketData] = useState<LatestPriceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMarketData = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await fetch('http://127.0.0.1:8000/api/v1/market/latest/RELIANCE');

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        setMarketData(data);
      } catch (err) {
        setError('API Error');
        setMarketData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchMarketData();

    // Set up auto-refresh every 30 seconds
    const interval = setInterval(fetchMarketData, 30000);

    return () => clearInterval(interval);
  }, []);

  const getFirstMetricValue = () => {
    if (loading) return 'Loading...';
    if (error) return 'API Error';
    return marketData?.close.toFixed(2) || '--';
  };

  const getFirstMetricDetail = () => {
    if (loading) return 'Fetching...';
    if (error) return 'Backend unavailable';
    if (marketData) {
      return `${marketData.symbol} | ${marketData.trade_date} | Vol: ${(marketData.volume / 1000000).toFixed(1)}M`;
    }
    return 'No data';
  };

  const firstMetric = {
    label: 'RELIANCE',
    value: getFirstMetricValue(),
    detail: getFirstMetricDetail(),
  };

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">MVP foundation</p>
          <h1>Market research dashboard</h1>
        </div>
      </header>
      <div className="metric-grid">
        <MetricCard key="reliance" {...firstMetric} />
        {otherMetrics.map((metric) => (
          <MetricCard key={metric.label} {...metric} />
        ))}
      </div>
      <section className="workspace-panel">
        <h2>Platform modules</h2>
        <div className="module-grid">
          <div>Market data API</div>
          <div>AI prediction API</div>
          <div>Backtesting API</div>
          <div>Trade history API</div>
        </div>
      </section>
    </section>
  );
}
