import type { ReactNode } from 'react';
import { BarChart3, BrainCircuit, BriefcaseBusiness, Gauge, LineChart, Settings, Telescope } from 'lucide-react';
import { NavLink } from 'react-router-dom';

const navItems = [
  { to: '/', label: 'Overview', icon: Gauge },
  { to: '/scanner', label: 'Scanner', icon: Telescope },
  { to: '/recommendations', label: 'AI Signals', icon: BrainCircuit },
  { to: '/portfolio', label: 'Portfolio', icon: BriefcaseBusiness },
  { to: '/backtesting', label: 'Backtests', icon: BarChart3 },
  { to: '/settings', label: 'Settings', icon: Settings },
];

type AppShellProps = {
  children: ReactNode;
};

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <LineChart aria-hidden="true" />
          <div>
            <strong>Vitta Quant AI</strong>
            <span>Indian markets</span>
          </div>
        </div>
        <nav className="nav-list" aria-label="Main navigation">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink key={item.to} to={item.to} className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
                <Icon aria-hidden="true" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </aside>
      <main className="main-content">{children}</main>
    </div>
  );
}
