import { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, ResponsiveContainer, Legend 
} from 'recharts';
import { useFilters } from '../contexts/FilterContext';
import OptimizationFilterBar from '../components/OptimizationFilterBar';

// Define the data types
interface CostDataPoint {
  period: string;
  actualModel: string;
  actualCost: number;
  alternativeModel: string;
  alternativeCost: number;
  savings: number;
  percentSavings: number;
  tokens: number;
}

// Format date for display
const formatDate = (date: Date) => {
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric'
  });
};

// Format hour for display
const formatHour = (hour: number) => {
  if (hour === 0) return '12 AM';
  if (hour === 12) return '12 PM';
  return hour < 12 ? `${hour} AM` : `${hour - 12} PM`;
};

// Get the first and last day of a week
const getWeekBounds = (date: Date) => {
  const dayOfWeek = date.getDay(); // 0 = Sunday, 6 = Saturday
  const firstDay = new Date(date);
  firstDay.setDate(date.getDate() - dayOfWeek); // Move to Sunday
  
  const lastDay = new Date(firstDay);
  lastDay.setDate(firstDay.getDate() + 6); // Move to Saturday
  
  return { firstDay, lastDay };
};

// Format date range for week display
const formatWeekRange = (startDate: Date, endDate: Date) => {
  const startMonth = startDate.toLocaleString('default', { month: 'short' });
  const endMonth = endDate.toLocaleString('default', { month: 'short' });
  const startDay = startDate.getDate();
  const endDay = endDate.getDate();
  
  if (startMonth === endMonth) {
    return `${startMonth} ${startDay}-${endDay}`;
  } else {
    return `${startMonth} ${startDay}-${endMonth} ${endDay}`;
  }
};

// Dummy data generator based on date range
const generateDummyData = (from: Date, to: Date, interval: string): CostDataPoint[] => {
  const data: CostDataPoint[] = [];
  
  // Clone the dates to avoid modifying the originals
  const startDate = new Date(from);
  const endDate = new Date(to);
  
  if (interval === 'day') {
    // For day view, generate 24 hours
    const selectedDate = new Date(to);
    
    // Generate data for every hour (0-23)
    for (let hour = 0; hour < 24; hour += 4) {
      // Only add data for every 4th hour to match the display intervals
      // We'll use empty data for other hours
      const value = hour === 16 ? Math.floor(Math.random() * 2000) + 500 : 0; // Only add significant data to 4pm
      const tokens = value;
      const actualCost = Math.round((tokens * 0.0000025) * 10000) / 10000;
      const alternativeCost = Math.round((actualCost * 0.65) * 10000) / 10000;
      const savings = Math.round((actualCost - alternativeCost) * 10000) / 10000;
      const percentSavings = tokens > 0 ? Math.round((savings / actualCost) * 1000) / 10 : 0;
      
      data.push({
        period: formatHour(hour),
        actualModel: 'claude-3-haiku',
        actualCost,
        alternativeModel: 'claude-2',
        alternativeCost,
        savings,
        percentSavings,
        tokens
      });
    }
  } 
  else if (interval === 'week') {
    // For week view, generate 7 days (Sun-Sat)
    const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const refDate = new Date(to);
    
    // Calculate the week's Sunday (start of week)
    const dayOfWeek = refDate.getDay();
    const sundayDate = new Date(refDate);
    sundayDate.setDate(refDate.getDate() - dayOfWeek);
    
    // Generate data for each day of the week
    for (let i = 0; i < 7; i++) {
      const currentDate = new Date(sundayDate);
      currentDate.setDate(sundayDate.getDate() + i);
      
      // Random data with more activity in the middle of the week
      const factor = i === 3 ? 5 : // Wednesday has 5x normal activity
                    i === 4 || i === 5 ? 2 : // Thu/Fri have 2x activity
                    1; // Other days have normal activity
      
      const tokens = Math.floor(Math.random() * 1000 + 500) * factor;
      const actualCost = Math.round((tokens * 0.0000025) * 10000) / 10000;
      const alternativeCost = Math.round((actualCost * 0.65) * 10000) / 10000;
      const savings = Math.round((actualCost - alternativeCost) * 10000) / 10000;
      const percentSavings = Math.round((savings / actualCost) * 1000) / 10;
      
      const day = currentDate.getDate();
      
      data.push({
        period: `${dayNames[i]} ${day}`,
        actualModel: 'claude-3-haiku',
        actualCost,
        alternativeModel: 'claude-2',
        alternativeCost,
        savings,
        percentSavings,
        tokens
      });
    }
  } 
  else if (interval === 'month') {
    // For month view, we'll now show weeks instead of days
    const month = to.getMonth();
    const year = to.getFullYear();
    const firstDayOfMonth = new Date(year, month, 1);
    const lastDayOfMonth = new Date(year, month + 1, 0);
    
    // Find the first Sunday on or before the first day of the month
    const firstSunday = new Date(firstDayOfMonth);
    const dayOfWeek = firstDayOfMonth.getDay();
    if (dayOfWeek > 0) {
      // If the month doesn't start on Sunday, go back to the previous Sunday
      firstSunday.setDate(firstDayOfMonth.getDate() - dayOfWeek);
    }
    
    // Generate data for each week that overlaps with the month
    let currentWeekStart = new Date(firstSunday);
    while (currentWeekStart <= lastDayOfMonth) {
      const weekEnd = new Date(currentWeekStart);
      weekEnd.setDate(currentWeekStart.getDate() + 6); // Saturday
      
      // Generate more activity in mid-month weeks
      const isMiddleOfMonth = 
        (currentWeekStart.getDate() >= 8 && currentWeekStart.getDate() <= 22) || 
        (weekEnd.getDate() >= 8 && weekEnd.getDate() <= 22);
      
      const factor = isMiddleOfMonth ? 3 : 1;
      const isMay13Week = (currentWeekStart.getDate() <= 13 && weekEnd.getDate() >= 13);
      
      // May 13 has a spike for visual interest
      const tokens = isMay13Week ? 25000 : Math.floor(Math.random() * 2000 + 1000) * factor;
      const actualCost = Math.round((tokens * 0.0000025) * 10000) / 10000;
      const alternativeCost = Math.round((actualCost * 0.65) * 10000) / 10000;
      const savings = Math.round((actualCost - alternativeCost) * 10000) / 10000;
      const percentSavings = Math.round((savings / actualCost) * 1000) / 10;
      
      const weekLabel = formatWeekRange(currentWeekStart, weekEnd);
      
      data.push({
        period: weekLabel,
        actualModel: 'claude-3-haiku',
        actualCost,
        alternativeModel: 'claude-2',
        alternativeCost,
        savings,
        percentSavings,
        tokens
      });
      
      // Move to next week
      currentWeekStart.setDate(currentWeekStart.getDate() + 7);
    }
  }
  else if (interval === 'year') {
    // For year view, show each month
    const year = to.getFullYear();
    const monthNames = [
      'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ];
    
    // Generate data for each month
    for (let month = 0; month < 12; month++) {
      // Generate more activity in spring/summer months (Mar-Aug)
      const isSpringOrSummer = month >= 2 && month <= 7;
      const factor = isSpringOrSummer ? 2 : 1;
      const isJune = month === 5; // June has a big spike
      
      const tokens = isJune ? 40000 : Math.floor(Math.random() * 5000 + 2000) * factor;
      const actualCost = Math.round((tokens * 0.0000025) * 10000) / 10000;
      const alternativeCost = Math.round((actualCost * 0.65) * 10000) / 10000;
      const savings = Math.round((actualCost - alternativeCost) * 10000) / 10000;
      const percentSavings = Math.round((savings / actualCost) * 1000) / 10;
      
      data.push({
        period: monthNames[month],
        actualModel: 'claude-3-haiku',
        actualCost,
        alternativeModel: 'claude-2',
        alternativeCost,
        savings,
        percentSavings,
        tokens
      });
    }
  }
  
  return data;
};

const CostOptimization = () => {
  const { filters } = useFilters();
  const [showSavings, setShowSavings] = useState(true);
  const [data, setData] = useState<CostDataPoint[]>([]);
  
  // Update data when filters change
  useEffect(() => {
    const newData = generateDummyData(filters.from, filters.to, filters.interval);
    setData(newData);
  }, [filters.from, filters.to, filters.interval, filters.task]);
  
  // Calculate totals
  const totalActualCost = data.reduce((sum, item) => sum + item.actualCost, 0);
  const totalAlternativeCost = data.reduce((sum, item) => sum + item.alternativeCost, 0);
  const totalSavings = data.reduce((sum, item) => sum + item.savings, 0);
  const averagePercentSavings = totalSavings / totalActualCost * 100 || 0; // Add fallback for initial empty state
  
  // Format as currency
  const formatCurrency = (value: number) => {
    return `$${value.toFixed(4)}`;
  };
  
  // Generate chart title based on interval
  const getChartTitle = () => {
    if (filters.interval === 'day') {
      // Format: "Hourly Usage (May 16, 2025)"
      const formattedDate = filters.to.toLocaleDateString('en-US', {
        month: 'long',
        day: 'numeric',
        year: 'numeric'
      });
      return `Cost Breakdown (${formattedDate})`;
    } 
    else if (filters.interval === 'week') {
      return 'Daily Cost Breakdown (Week)';
    } 
    else if (filters.interval === 'month') {
      return 'Weekly Cost Breakdown (Month)';
    }
    else if (filters.interval === 'year') {
      return 'Monthly Cost Breakdown (Year)';
    }
    return 'Cost Breakdown by Period';
  };
  
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold mb-2">Cost Optimization</h1>
      
      {/* Global Filter Bar */}
      <OptimizationFilterBar />
      
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gray-50 p-4 rounded-md">
          <h3 className="text-sm font-medium text-gray-500 mb-1">Current Cost</h3>
          <p className="text-2xl font-bold">{formatCurrency(totalActualCost)}</p>
          <p className="text-xs text-gray-500 mt-1">Using claude-3-haiku</p>
        </div>
        
        <div className="bg-gray-50 p-4 rounded-md">
          <h3 className="text-sm font-medium text-gray-500 mb-1">Potential Cost</h3>
          <p className="text-2xl font-bold">{formatCurrency(totalAlternativeCost)}</p>
          <p className="text-xs text-gray-500 mt-1">Using claude-2</p>
        </div>
        
        <div className="bg-gray-50 p-4 rounded-md">
          <h3 className="text-sm font-medium text-gray-500 mb-1">Potential Savings</h3>
          <p className="text-2xl font-bold text-green-600">{formatCurrency(totalSavings)}</p>
          <p className="text-xs text-gray-500 mt-1">~{averagePercentSavings.toFixed(1)}% less expensive</p>
        </div>
      </div>
      
      {/* Cost Comparison Chart */}
      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">{getChartTitle()}</h2>
          <button 
            className="btn btn-outline text-xs"
            onClick={() => setShowSavings(!showSavings)}
          >
            {showSavings ? 'Hide Savings' : 'Show Savings'}
          </button>
        </div>
        
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={data}
              margin={{ top: 10, right: 30, left: 20, bottom: 25 }}
            >
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis 
                dataKey="period" 
                tick={{ fontSize: 12 }}
                height={40}
                // Interval logic based on the time period
                interval={filters.interval === 'day' ? 1 : // Every 4 hours (already filtered in data)
                         filters.interval === 'year' ? 0 : // Show all months
                         0} // Show all periods for week and month
                tickMargin={8}
                // For month and year views, we may need to rotate labels
                angle={filters.interval === 'month' ? -20 : 0}
                textAnchor={filters.interval === 'month' ? 'end' : 'middle'}
              />
              <YAxis 
                tickFormatter={(value) => `$${value.toFixed(3)}`}
                width={60}
                tick={{ fontSize: 12 }}
              />
              <Tooltip 
                formatter={(value, name) => {
                  if (name === 'alternativeCost') return [`$${Number(value).toFixed(4)}`, 'Alternative Model Cost'];
                  if (name === 'savings') return [`$${Number(value).toFixed(4)}`, 'Potential Savings'];
                  return [value, name];
                }}
                labelFormatter={(label) => {
                  if (filters.interval === 'day') {
                    // For day view, show date with hour
                    const selectedDate = filters.to.toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric'
                    });
                    return `${selectedDate}, ${label}`;
                  }
                  else if (filters.interval === 'year') {
                    // For year view, show month name with year
                    return `${label} ${filters.to.getFullYear()}`;
                  }
                  // For other views, just use the label
                  return `Period: ${label}`;
                }}
              />
              <Legend />
              <Bar 
                dataKey="alternativeCost" 
                name="Alternative Cost" 
                stackId="a"
                fill="#6366F1" 
                radius={[0, 0, 0, 0]}
              />
              <Bar 
                dataKey="savings" 
                name="Potential Savings" 
                stackId="a"
                fill="#A5B4FC" 
                radius={[4, 4, 0, 0]}
                hide={!showSavings}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="text-xs text-gray-500 mt-2 text-center">
          Each bar represents the current cost, broken down into alternative cost (darker) and potential savings (lighter).
        </div>
      </div>
      
      {/* Detailed Table */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Cost Optimization Details</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm divide-y divide-gray-200">
            <thead>
              <tr className="text-left text-gray-500">
                <th className="py-2">Period</th>
                <th className="py-2">Current Model</th>
                <th className="py-2 text-right">Current Cost</th>
                <th className="py-2">Alternative Model</th>
                <th className="py-2 text-right">Alternative Cost</th>
                <th className="py-2 text-right">Savings</th>
                <th className="py-2 text-right">% Savings</th>
                <th className="py-2 text-right">Tokens</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {data.filter(row => row.tokens > 0).map((row, i) => (
                <tr key={i} className="hover:bg-gray-50">
                  <td className="py-2">{row.period}</td>
                  <td className="py-2">{row.actualModel}</td>
                  <td className="py-2 text-right">{formatCurrency(row.actualCost)}</td>
                  <td className="py-2">{row.alternativeModel}</td>
                  <td className="py-2 text-right">{formatCurrency(row.alternativeCost)}</td>
                  <td className="py-2 text-right text-green-600">{formatCurrency(row.savings)}</td>
                  <td className="py-2 text-right">{row.percentSavings.toFixed(1)}%</td>
                  <td className="py-2 text-right">{row.tokens.toLocaleString()}</td>
                </tr>
              ))}
              {/* Totals row */}
              <tr className="bg-gray-50 font-medium">
                <td colSpan={2} className="py-2">Total</td>
                <td className="py-2 text-right">{formatCurrency(totalActualCost)}</td>
                <td></td>
                <td className="py-2 text-right">{formatCurrency(totalAlternativeCost)}</td>
                <td className="py-2 text-right text-green-600">{formatCurrency(totalSavings)}</td>
                <td className="py-2 text-right">{averagePercentSavings.toFixed(1)}%</td>
                <td className="py-2 text-right">{data.reduce((sum, item) => sum + item.tokens, 0).toLocaleString()}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      {/* Recommendation Section */}
      <div className="card bg-blue-50">
        <h2 className="text-lg font-semibold mb-2">Recommendation</h2>
        <p className="text-sm mb-4">
          Based on your usage patterns, switching from <span className="font-medium">claude-3-haiku</span> to <span className="font-medium">claude-2</span> for 
          certain tasks could reduce costs by approximately <span className="font-medium text-green-600">{averagePercentSavings.toFixed(1)}%</span>.
        </p>
        <div className="flex gap-2">
          <button className="btn bg-blue-600 hover:bg-blue-700 text-white">Apply Recommendation</button>
          <button className="btn btn-outline">Learn More</button>
        </div>
      </div>
    </div>
  );
};

export default CostOptimization; 