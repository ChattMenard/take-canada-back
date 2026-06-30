import { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function VaccineWasteChart() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch('/api/visualization/vaccine-waste')
      .then(res => res.json())
      .then(setData)
      .catch(err => console.error('Failed to load vaccine waste data:', err));
  }, []);

  if (!data) return <div className="text-slate-400">Loading...</div>;

  const chartData = [
    { name: 'Purchased', value: data.purchased, color: '#3b82f6' },
    { name: 'Administered', value: data.administered, color: '#22c55e' },
    { name: 'Wasted', value: data.wasted, color: '#ef4444' },
    { name: 'Expired', value: data.expired, color: '#f97316' },
    { name: 'Donated', value: data.donated, color: '#8b5cf6' },
  ];

  return (
    <div className="w-full bg-gradient-to-br from-slate-900 to-slate-800 p-8 rounded-lg">
      <h2 className="text-2xl font-bold text-white mb-6">Vaccine Waste Analysis</h2>
      
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
          <XAxis dataKey="name" stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" tickFormatter={(value) => `${(value / 1000000).toFixed(0)}M`} />
          <Tooltip 
            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }}
            formatter={(value) => [`${(value / 1000000).toFixed(1)}M doses`, '']}
          />
          <Legend />
          {chartData.map((entry, index) => (
            <Bar key={index} dataKey="value" fill={entry.color} />
          ))}
        </BarChart>
      </ResponsiveContainer>

      <div className="mt-6 grid grid-cols-2 gap-4">
        <div className="bg-red-900/30 border border-red-500 p-4 rounded-lg">
          <div className="text-red-400 font-bold">Total Waste Cost</div>
          <div className="text-red-300 text-2xl">${data.waste_cost_billion}B</div>
        </div>
        <div className="bg-slate-700 p-4 rounded-lg">
          <div className="text-slate-400 font-bold">Cost Per Dose</div>
          <div className="text-white text-2xl">${data.per_dose_cost}</div>
        </div>
      </div>

      <div className="mt-4 text-xs text-slate-400">
        Source: {data.source}
      </div>
    </div>
  );
}
