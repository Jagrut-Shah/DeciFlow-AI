"use client";

import React from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, AreaChart, Area, PieChart, Pie, Cell, Legend
} from 'recharts';

interface ChartProps {
  config: {
    type: 'bar' | 'line' | 'area' | 'pie';
    title: string;
    data: Array<{ name: string; value: number }>;
    description?: string;
  };
}

const COLORS = ['#2563EB', '#16A87A', '#F59E0B', '#E84444', '#1B2B4B', '#4A5568'];

export default function DynamicChart({ config }: ChartProps) {
  if (!config || !config.data || config.data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center bg-ice-blue dark:bg-white/5 rounded-2xl border border-dashed border-cool-gray dark:border-white/10">
        <p className="text-muted-text text-sm">Waiting for visualization data...</p>
      </div>
    );
  }

  const renderChart = () => {
    switch (config.type) {
      case 'line':
        return (
          <LineChart data={config.data}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
            <XAxis 
              dataKey="name" 
              axisLine={false} 
              tickLine={false} 
              tick={{ fill: 'var(--muted-text)', fontSize: 10 }}
              dy={10}
            />
            <YAxis 
              axisLine={false} 
              tickLine={false} 
              tick={{ fill: 'var(--muted-text)', fontSize: 10 }} 
            />
            <Tooltip 
              contentStyle={{ backgroundColor: 'var(--navy)', border: 'none', borderRadius: '12px', fontSize: '12px' }}
              itemStyle={{ color: '#fff' }}
            />
            <Line 
              type="monotone" 
              dataKey="value" 
              stroke="var(--sapphire)" 
              strokeWidth={3} 
              dot={{ r: 4, fill: 'var(--sapphire)', strokeWidth: 2, stroke: '#fff' }}
              activeDot={{ r: 6, strokeWidth: 0 }}
            />
          </LineChart>
        );
      case 'area':
        return (
          <AreaChart data={config.data}>
            <defs>
              <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="var(--sapphire)" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="var(--sapphire)" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
            <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: 'var(--muted-text)', fontSize: 10 }} dy={10} />
            <YAxis axisLine={false} tickLine={false} tick={{ fill: 'var(--muted-text)', fontSize: 10 }} />
            <Tooltip 
              contentStyle={{ backgroundColor: 'var(--navy)', border: 'none', borderRadius: '12px', fontSize: '12px' }}
              itemStyle={{ color: '#fff' }}
            />
            <Area type="monotone" dataKey="value" stroke="var(--sapphire)" fillOpacity={1} fill="url(#colorValue)" strokeWidth={3} />
          </AreaChart>
        );
      case 'pie':
        return (
          <PieChart>
            <Pie
              data={config.data}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={80}
              paddingAngle={5}
              dataKey="value"
            >
              {config.data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip 
               contentStyle={{ backgroundColor: 'var(--navy)', border: 'none', borderRadius: '12px', fontSize: '12px' }}
               itemStyle={{ color: '#fff' }}
            />
            <Legend verticalAlign="bottom" height={36}/>
          </PieChart>
        );
      case 'bar':
      default:
        return (
          <BarChart data={config.data}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
            <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: 'var(--muted-text)', fontSize: 10 }} dy={10} />
            <YAxis axisLine={false} tickLine={false} tick={{ fill: 'var(--muted-text)', fontSize: 10 }} />
            <Tooltip 
              cursor={{ fill: 'rgba(255,255,255,0.05)' }}
              contentStyle={{ backgroundColor: 'var(--navy)', border: 'none', borderRadius: '12px', fontSize: '12px' }}
              itemStyle={{ color: '#fff' }}
            />
            <Bar dataKey="value" fill="var(--sapphire)" radius={[4, 4, 0, 0]} />
          </BarChart>
        );
    }
  };

  return (
    <div className="w-full">
      <div className="flex flex-col mb-6">
        <h3 className="text-xl font-bold text-navy dark:text-white">{config.title}</h3>
        {config.description && <p className="text-sm text-muted-text dark:text-white/60 mt-1">{config.description}</p>}
      </div>
      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          {renderChart()}
        </ResponsiveContainer>
      </div>
    </div>
  );
}
