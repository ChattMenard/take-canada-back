import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

export default function MoneyFlowSankey() {
  const [flows, setFlows] = useState([]);

  useEffect(() => {
    fetch('/api/visualization/financial-flow')
      .then(res => res.json())
      .then(data => setFlows(data.flows || []))
      .catch(err => console.error('Failed to load financial flows:', err));
  }, []);

  // Calculate total for flow thickness
  const totalAmount = flows.reduce((sum, flow) => sum + flow.amount, 0);

  return (
    <div className="w-full bg-gradient-to-br from-slate-900 to-slate-800 p-8 rounded-lg">
      <h2 className="text-2xl font-bold text-white mb-6">$5-9B Vaccine Contract Money Trail</h2>
      
      <div className="flex justify-between items-center h-64 relative">
        {/* Source: Canadian Taxpayers */}
        <motion.div
          initial={{ x: -50, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          className="w-48 bg-blue-600 p-4 rounded-lg text-center"
        >
          <div className="text-white font-bold">Canadian Taxpayers</div>
          <div className="text-blue-200 text-sm">$9B Budgeted</div>
        </motion.div>

        {/* Middle: Government Procurement */}
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="w-48 bg-slate-700 p-4 rounded-lg text-center border-2 border-slate-500"
        >
          <div className="text-white font-bold">Government</div>
          <div className="text-slate-300 text-sm">Procurement</div>
          <div className="text-slate-400 text-xs mt-2">Black Box</div>
        </motion.div>

        {/* Right: Pharma Companies */}
        <div className="flex flex-col gap-4">
          {['Pfizer', 'Moderna'].map((company, index) => (
            <motion.div
              key={company}
              initial={{ x: 50, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: index * 0.2 }}
              className="w-48 bg-red-600 p-4 rounded-lg text-center"
            >
              <div className="text-white font-bold">{company}</div>
              <div className="text-red-200 text-sm">~$2.5B Each</div>
            </motion.div>
          ))}
        </div>

        {/* Flow lines */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none">
          <defs>
            <linearGradient id="flowGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#3b82f6" />
              <stop offset="50%" stopColor="#64748b" />
              <stop offset="100%" stopColor="#dc2626" />
            </linearGradient>
          </defs>
          
          {/* Taxpayers to Government */}
          <motion.path
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            d="M 200 128 L 350 128"
            stroke="url(#flowGradient)"
            strokeWidth="20"
            fill="none"
            opacity="0.6"
          />
          
          {/* Government to Pfizer */}
          <motion.path
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ delay: 0.3 }}
            d="M 450 128 C 550 128, 550 80, 650 80"
            stroke="url(#flowGradient)"
            strokeWidth="10"
            fill="none"
            opacity="0.6"
          />
          
          {/* Government to Moderna */}
          <motion.path
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ delay: 0.5 }}
            d="M 450 128 C 550 128, 550 176, 650 176"
            stroke="url(#flowGradient)"
            strokeWidth="10"
            fill="none"
            opacity="0.6"
          />
        </svg>
      </div>

      {/* Waste indicator */}
      <div className="mt-6 bg-red-900/30 border border-red-500 p-4 rounded-lg">
        <div className="text-red-400 font-bold">$1-1.2B Wasted</div>
        <div className="text-red-300 text-sm">40M doses destroyed at $25-30/dose</div>
      </div>
    </div>
  );
}
