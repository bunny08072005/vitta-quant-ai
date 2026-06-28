import { MetricCard } from '../components/ui/MetricCard';

const metrics = [
  { label: 'Nifty 50', value: '--', detail: 'Market feed pending' },
  { label: 'Active Models', value: '0', detail: 'Training not configured' },
  { label: 'Signals Today', value: '0', detail: 'Inference disabled' },
  { label: 'Backtests', value: '0', detail: 'Engine scaffolded' },
];

export function DashboardPage() {
  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">MVP foundation</p>
          <h1>Market research dashboard</h1>
        </div>
      </header>
      <div className="metric-grid">
        {metrics.map((metric) => (
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
