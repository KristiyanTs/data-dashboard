import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { fetchStatistics } from '../services/api';
import './Dashboard.css';

export function Dashboard() {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['statistics'],
    queryFn: fetchStatistics,
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  if (isLoading) {
    return (
      <div className="dashboard">
        <div className="loading">
          <span className="loading-spinner" aria-hidden />
          Loading statistics…
        </div>
      </div>
    );
  }
  if (error) return <div className="dashboard"><div className="error">Error loading statistics</div></div>;
  if (!stats) return null;

  const chartData = Object.entries(stats.by_category).map(([category, data]) => ({
    name: category.charAt(0).toUpperCase() + category.slice(1),
    count: data.count,
    value: data.total_value,
  }));

  const chartColors = { count: '#0f766e', value: '#0d9488' };

  return (
    <div className="dashboard">
      <h2 className="dashboard-title">Dashboard</h2>

      <div className="stats-grid">
        <div className="stat-card">
          <h3 className="stat-card-label">Total contracts</h3>
          <p className="stat-card-value">{stats.total_contracts.toLocaleString()}</p>
        </div>
        <div className="stat-card">
          <h3 className="stat-card-label">Total value</h3>
          <p className="stat-card-value">
            ${stats.total_value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
        </div>
        <div className="stat-card">
          <h3 className="stat-card-label">Average value</h3>
          <p className="stat-card-value">
            ${stats.average_value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
        </div>
      </div>

      {chartData.length > 0 && (
        <div className="chart-container">
          <h3>Contracts by category</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData} margin={{ top: 8, right: 8, bottom: 8, left: 8 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
              <XAxis dataKey="name" stroke="var(--color-text-muted)" fontSize={12} tickLine={false} />
              <YAxis yAxisId="left" orientation="left" stroke="var(--color-text-muted)" fontSize={12} tickLine={false} />
              <YAxis yAxisId="right" orientation="right" stroke="var(--color-text-muted)" fontSize={12} tickLine={false} />
              <Tooltip
                contentStyle={{ borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}
                labelStyle={{ color: 'var(--color-text)' }}
              />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Bar yAxisId="left" dataKey="count" fill={chartColors.count} name="Count" radius={[4, 4, 0, 0]} />
              <Bar yAxisId="right" dataKey="value" fill={chartColors.value} name="Total value ($)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
