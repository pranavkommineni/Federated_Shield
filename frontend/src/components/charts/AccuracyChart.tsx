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

export const AccuracyChart: React.FC<AccuracyChartProps> = ({ data, height = 320 }) => {
  const chartData = data.map((item) => ({
    round: `R${item.roundNumber}`,
    accuracy: Math.round(item.accuracy * 1000) / 10,
    loss: Math.round(item.loss * 1000) / 1000,
    epsilon: Math.round(item.cumulativeEpsilon * 100) / 100,
  }));

  if (chartData.length === 0) {
    return (
      <div className="h-[320px] flex flex-col items-center justify-center text-slate-500 border border-dashed border-slate-800 rounded-xl">
        <p className="text-sm font-medium">No training rounds recorded yet</p>
        <p className="text-xs text-slate-600 mt-1">Start a training round to stream live accuracy and loss curves</p>
      </div>
    );
  }

  return (
    <div style={{ width: '100%', height, minHeight: height }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="accGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#00f2fe" stopOpacity={0.35} />
              <stop offset="95%" stopColor="#00f2fe" stopOpacity={0.0} />
            </linearGradient>
            <linearGradient id="lossGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#a855f7" stopOpacity={0.35} />
              <stop offset="95%" stopColor="#a855f7" stopOpacity={0.0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
          <XAxis dataKey="round" stroke="#64748b" tick={{ fontSize: 12, fontFamily: 'JetBrains Mono' }} />
          <YAxis
            yAxisId="left"
            stroke="#00f2fe"
            domain={[0, 100]}
            tick={{ fontSize: 12, fontFamily: 'JetBrains Mono' }}
            unit="%"
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            stroke="#a855f7"
            domain={[0, 'auto']}
            tick={{ fontSize: 12, fontFamily: 'JetBrains Mono' }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#0e1526',
              borderColor: 'rgba(255,255,255,0.1)',
              borderRadius: '12px',
              color: '#f8fafc',
              fontFamily: 'Inter',
            }}
          />
          <Legend
            verticalAlign="top"
            align="right"
            wrapperStyle={{ paddingBottom: '10px', fontSize: '12px' }}
          />
          <Area
            yAxisId="left"
            type="monotone"
            dataKey="accuracy"
            name="Global Accuracy (%)"
            stroke="#00f2fe"
            strokeWidth={3}
            fillOpacity={1}
            fill="url(#accGradient)"
          />
          <Area
            yAxisId="right"
            type="monotone"
            dataKey="loss"
            name="Global Loss"
            stroke="#a855f7"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#lossGradient)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};
