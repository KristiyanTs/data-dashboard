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

  if (isLoading) return <div className="loading">Loading statistics...</div>;
  if (error) return <div className="error">Error loading statistics</div>;
  if (!stats) return null;

  const chartData = Object.entries(stats.by_category).map(([category, data]) => ({
    name: category.charAt(0).toUpperCase() + category.slice(1),
    count: data.count,
    value: data.total_value,
  }));

  return (
    <div className="dashboard">
      <h2>Dashboard</h2>
      
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Contracts</h3>
          <p className="stat-value">{stats.total_contracts.toLocaleString()}</p>
        </div>
        <div className="stat-card">
          <h3>Total Value</h3>
          <p className="stat-value">${stats.total_value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
        </div>
        <div className="stat-card">
          <h3>Average Value</h3>
          <p className="stat-value">${stats.average_value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
        </div>
      </div>

      {chartData.length > 0 && (
        <div className="chart-container">
          <h3>Contracts by Category</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis yAxisId="left" orientation="left" stroke="#8884d8" />
              <YAxis yAxisId="right" orientation="right" stroke="#82ca9d" />
              <Tooltip />
              <Legend />
              <Bar yAxisId="left" dataKey="count" fill="#8884d8" name="Count" />
              <Bar yAxisId="right" dataKey="value" fill="#82ca9d" name="Total Value ($)" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
