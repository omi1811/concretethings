'use client';

import { ArrowUpIcon, ArrowDownIcon } from 'lucide-react';

export default function KPICard({ 
  title, 
  value, 
  change, 
  trend, 
  icon: Icon,
  color = 'blue' 
}) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600 border-blue-200',
    green: 'bg-green-50 text-green-600 border-green-200',
    yellow: 'bg-yellow-50 text-yellow-600 border-yellow-200',
    red: 'bg-red-50 text-red-600 border-red-200',
    purple: 'bg-purple-50 text-purple-600 border-purple-200',
  };

  const trendColor = trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-gray-600';

  return (
    <div className={`rounded-lg border-2 p-6 ${colorClasses[color]} transition-all hover:shadow-lg`}>
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium opacity-80">{title}</p>
          <p className="text-3xl font-bold mt-2">{value}</p>
          
          {change !== undefined && (
            <div className={`flex items-center mt-3 ${trendColor}`}>
              {trend === 'up' && <ArrowUpIcon className="w-4 h-4 mr-1" />}
              {trend === 'down' && <ArrowDownIcon className="w-4 h-4 mr-1" />}
              <span className="text-sm font-semibold">{change}%</span>
              <span className="text-xs ml-1 opacity-70">vs last month</span>
            </div>
          )}
        </div>
        
        {Icon && (
          <div className="ml-4">
            <Icon className="w-12 h-12 opacity-50" />
          </div>
        )}
      </div>
    </div>
  );
}
