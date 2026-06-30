import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import * as d3 from 'd3';

export default function HeroTimeline() {
  const [events, setEvents] = useState([]);
  const [hoveredEvent, setHoveredEvent] = useState(null);

  useEffect(() => {
    // Load timeline data
    fetch('/api/visualization/timeline')
      .then(res => res.json())
      .then(data => setEvents(data.events || []))
      .catch(err => console.error('Failed to load timeline:', err));
  }, []);

  // Smoking gun: Dec 12, 2019 to Dec 31, 2019 (19 days)
  const smokingGunStart = new Date('2019-12-12');
  const smokingGunEnd = new Date('2019-12-31');

  return (
    <div className="w-full bg-gradient-to-br from-slate-900 to-slate-800 p-8 rounded-lg">
      <h2 className="text-2xl font-bold text-white mb-6">The Smoking Gun Timeline</h2>
      
      <div className="relative h-64">
        {/* Timeline base */}
        <div className="absolute top-1/2 left-0 right-0 h-1 bg-slate-600 transform -translate-y-1/2" />
        
        {/* Smoking gun zone */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="absolute top-0 bottom-0 bg-red-500/20 border-2 border-red-500 rounded"
          style={{
            left: `${d3.scaleTime().domain([new Date('2013-01-01'), new Date('2020-12-31')]).range([0, 100])(smokingGunStart)}%`,
            width: `${d3.scaleTime().domain([new Date('2013-01-01'), new Date('2020-12-31')]).range([0, 100])(smokingGunEnd) - d3.scaleTime().domain([new Date('2013-01-01'), new Date('2020-12-31')]).range([0, 100])(smokingGunStart)}%`
          }}
        >
          <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 text-red-400 text-sm font-bold whitespace-nowrap">
            19 Days Before COVID
          </div>
        </motion.div>

        {/* Timeline events */}
        {events.map((event, index) => {
          const date = new Date(event.date);
          const position = d3.scaleTime()
            .domain([new Date('2013-01-01'), new Date('2020-12-31')])
            .range([0, 100])(date);

          const isSmokingGun = date >= smokingGunStart && date <= smokingGunEnd;

          return (
            <motion.div
              key={index}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: index * 0.1 }}
              className="absolute top-1/2 transform -translate-y-1/2 cursor-pointer group"
              style={{ left: `${position}%` }}
              onMouseEnter={() => setHoveredEvent(event)}
              onMouseLeave={() => setHoveredEvent(null)}
            >
              <div className={`
                w-4 h-4 rounded-full border-2 transition-all
                ${isSmokingGun ? 'bg-red-500 border-red-400 animate-pulse' : 'bg-blue-500 border-blue-400'}
                group-hover:scale-150
              `} />
              
              {hoveredEvent === event && (
                <motion.div
                  initial={{ opacity: 0, y: 0 }}
                  animate={{ opacity: 1, y: -10 }}
                  className="absolute bottom-6 left-1/2 transform -translate-x-1/2 bg-slate-800 p-3 rounded-lg shadow-xl w-64 z-10"
                >
                  <div className="text-white font-bold text-sm">{event.title}</div>
                  <div className="text-slate-300 text-xs mt-1">{event.date}</div>
                  <div className="text-slate-400 text-xs mt-2">{event.description.substring(0, 100)}...</div>
                  <div className="text-xs text-blue-400 mt-2 uppercase">{event.category}</div>
                </motion.div>
              )}
            </motion.div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="flex gap-6 mt-8 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-green-500" />
          <span className="text-slate-300">Funding</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-orange-500" />
          <span className="text-slate-300">Simulation</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-red-500" />
          <span className="text-slate-300">Activation</span>
        </div>
      </div>
    </div>
  );
}
