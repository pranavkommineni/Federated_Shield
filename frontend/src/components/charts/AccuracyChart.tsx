import React from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import { RoundMetric } from '../../types/training';

interface AccuracyChartProps {
  data: RoundMetric[];
  height?: number;
}

export const AccuracyChart: React.FC<AccuracyChartProps> = ({ data, height = 300 }) => {
  const chartData = data.map((item) => ({
    round: `R${item.roundNumber}`,
    accuracy: Math.round(item.accuracy * 1000) / 10,
    loss: Math.round(item.loss * 1000) / 1000,
    epsilon: Math.round(item.cumulativeEpsilon * 100) / 100,
  }));

  if (chartData.length === 0) {
    return (
      <div className="h-[300px] flex flex-col items-center justify-center text-slate-400 border border-dashed border-slate-200 rounded-xl">
        <p className="text-xs font-medium">No training rounds recorded yet</p>
        <p className="text-[11px] text-slate-500 mt-1">Start a training round to view accuracy & loss curves</p>
      </div>
    );
  }

  return (
    <div style={{ width: '100%', height, minHeight: height }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="accGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#2563eb" stopOpacity={0.15} />
              <stop offset="95%" stopColor="#2563eb" stopOpacity={0.0} />
            </linearGradient>
            <linearGradient id="lossGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#7c3aed" stopOpacity={0.15} />
              <stop offset="95%" stopColor="#7c3aed" stopOpacity={0.0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
          <XAxis dataKey="round" stroke="#94a3b8" tick={{ fontSize: 11 }} />
          <YAxis
            yAxisId="left"
            stroke="#2563eb"
            domain={[0, 100]}
            tick={{ fontSize: 11 }}
            unit="%"
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            stroke="#7c3aed"
            domain={[0, 'auto']}
            tick={{ fontSize: 11 }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#ffffff',
              borderColor: '#e2e8f0',
              borderRadius: '8px',
              color: '#0f172a',
              fontSize: '12px',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
            }}
          />
          <Legend
            verticalAlign="top"
            align="right"
            wrapperStyle={{ paddingBottom: '8px', fontSize: '11px' }}
          />
          <Area
            yAxisId="left"
            type="monotone"
            dataKey="accuracy"
            name="Global Accuracy (%)"
            stroke="#2563eb"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#accGradient)"
          />
          <Area
            yAxisId="right"
            type="monotone"
            dataKey="loss"
            name="Global Loss"
            stroke="#7c3aed"
            strokeWidth={1.5}
            fillOpacity={1}
            fill="url(#lossGradient)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};
