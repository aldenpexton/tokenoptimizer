import { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, ResponsiveContainer, Legend 
} from 'recharts';
import { useFilters } from '../contexts/FilterContext';
import OptimizationFilterBar from '../components/OptimizationFilterBar';
import { fetchCostOptimization } from '../api/analytics';
import type { CostDataPoint, CostOptimizationData } from '../api/analytics';

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

const CostOptimization = () => {
  const { filters } = useFilters();
  const [showSavings, setShowSavings] = useState(true);
  const [data, setData] = useState<CostDataPoint[]>([]);
  const [summaryData, setSummaryData] = useState<CostOptimizationData['summary'] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Format date for API request
  const formatDateParam = (date: Date) => date.toISOString().split('T')[0];
  
  // Update data when filters change
  // Create empty hourly data points for day view
  const generateEmptyHourlyData = () => {
    const selectedDate = new Date(filters.to);
    const formattedDate = selectedDate.toLocaleDateString('en-US', { 
      month: 'short', day: 'numeric', year: 'numeric' 
    });
    
    const emptyData: CostDataPoint[] = [];
    
    // Generate all 24 hours
    for (let hour = 0; hour < 24; hour++) {
      const period = hour >= 12 ? 'PM' : 'AM';
      const hour12 = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour;
      const displayName = `${hour12} ${period}`;
      
      emptyData.push({
        period: displayName,
        display_date: `${formattedDate}, ${displayName}`,
        actualModel: filters.model !== '*' ? filters.model : '',
        alternativeModel: '',
        actualCost: 0,
        alternativeCost: 0,
        savings: 0,
        percentSavings: 0,
        tokens: 0
      });
    }
    
    return emptyData;
  };
  
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Get the date range from filters
        let fromParam = formatDateParam(filters.from);
        let toParam = formatDateParam(filters.to);
        
        // Adjust date parameters based on interval - match TokenUsageChart behavior
        if (filters.interval === 'day') {
          // For day view: use the same date for from/to to ensure we get hourly data
          // The backend expects the same date for both to show all hours of that day
          const refDate = new Date(filters.to);
          const dayDate = new Date(refDate.getFullYear(), refDate.getMonth(), refDate.getDate());
          fromParam = formatDateParam(dayDate);
          toParam = formatDateParam(dayDate);
          console.log(`Day view: Using single date ${toParam} for hourly breakdown`);
        } else if (filters.interval === 'month') {
          // For month view: ensure we're using the full month
          const year = filters.to.getFullYear();
          const month = filters.to.getMonth();
          const firstDay = new Date(year, month, 1);
          const lastDay = new Date(year, month + 1, 0);
          fromParam = formatDateParam(firstDay);
          toParam = formatDateParam(lastDay);
          console.log(`Month view: Using full month from ${fromParam} to ${toParam}`);
        } else if (filters.interval === 'week') {
          // For week view: ensure we're showing Sun-Sat
          const refDate = new Date(filters.to);
          const dayOfWeek = refDate.getDay(); // 0=Sun, 6=Sat
          const sunday = new Date(refDate);
          sunday.setDate(refDate.getDate() - dayOfWeek);
          const saturday = new Date(sunday);
          saturday.setDate(sunday.getDate() + 6);
          fromParam = formatDateParam(sunday);
          toParam = formatDateParam(saturday);
          console.log(`Week view: Using week from ${fromParam} to ${toParam}`);
        } else if (filters.interval === 'year') {
          // For year view: ensure we're using Jan 1 - Dec 31
          const year = filters.to.getFullYear();
          fromParam = `${year}-01-01`;
          toParam = `${year}-12-31`;
          console.log(`Year view: Using year from ${fromParam} to ${toParam}`);
        }
        
        console.log(`Fetching cost optimization: ${fromParam} to ${toParam}, interval=${filters.interval}`);
        
        // Call the API
        const result = await fetchCostOptimization(
          fromParam,
          toParam,
          filters.interval as 'day' | 'week' | 'month' | 'year',
          filters.model,
          filters.task
        );
        
        // If we got data, use it
        if (result && result.data) {
          // For day view, we need to ensure all 24 hours are present
          if (filters.interval === 'day') {
            // Generate all 24 empty hour slots
            const emptyHourlyData = generateEmptyHourlyData();
            
            // Merge with actual data - preserve actual data values where they exist
            if (result.data.length > 0) {
              result.data.forEach(dataPoint => {
                // Find corresponding empty data point by period
                const index = emptyHourlyData.findIndex(d => d.period === dataPoint.period);
                if (index >= 0) {
                  emptyHourlyData[index] = dataPoint;
                }
              });
            }
            
            setData(emptyHourlyData);
          } else {
            setData(result.data);
          }
          
          setSummaryData(result.summary);
        } else {
          // If no data, for day view, generate empty hourly data
          if (filters.interval === 'day') {
            setData(generateEmptyHourlyData());
          } else {
            setData([]);
          }
          
          setSummaryData({
            totalActualCost: 0,
            totalAlternativeCost: 0,
            totalSavings: 0,
            percentSavings: 0
          });
        }
      } catch (err) {
        console.error('Error fetching cost optimization data:', err);
        setError('Failed to load cost optimization data');
        setData([]);
        setSummaryData(null);
      } finally {
        setLoading(false);
      }
    };
    
    loadData();
  }, [filters.from, filters.to, filters.interval, filters.model, filters.task]);
  
  // Calculate totals from summaryData
  const totalActualCost = summaryData?.totalActualCost || 0;
  const totalAlternativeCost = summaryData?.totalAlternativeCost || 0;
  const totalSavings = summaryData?.totalSavings || 0;
  const averagePercentSavings = summaryData?.percentSavings || 0;
  
  // Format as currency
  const formatCurrency = (value: number) => {
    return `$${value.toFixed(4)}`;
  };
  
  // Generate chart title based on interval
  const getChartTitle = () => {
    if (filters.interval === 'day') {
      return `Hourly Usage (${filters.to.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })})`;
    } 
    else if (filters.interval === 'week') {
      return 'Daily Usage (Week)';
    } 
    else if (filters.interval === 'month') {
      return 'Daily Usage (Month)';
    }
    else if (filters.interval === 'year') {
      return 'Monthly Usage (Year)';
    }
    return 'Usage Over Time';
  };
  
  // Format value for Y-axis to handle small numbers better
  const formatYAxisValue = (value: number) => {
    if (value === 0) return '$0.000';
    if (value < 0.001) return `$${value.toFixed(5)}`;
    return `$${value.toFixed(3)}`;
  };
  
  // Determine if the data is extremely small
  const maxValue = Math.max(...data.map(d => Math.max(d.actualCost, 0)));
  const isSmallData = maxValue > 0 && maxValue < 0.01;

  // Set bar size based on data scale
  const barSize = isSmallData ? 40 : 30;
  
  // Generate data summary for display beneath the chart
  const getDataSummary = () => {
    if (!data || data.length === 0) return "No data available";
    
    // Format: "Data: May 13: 350, May 14: 10517, May 15: 2594, May 16: 2200"
    const nonZeroItems = data.filter(item => item.tokens > 0);
    
    if (nonZeroItems.length === 0) {
      return "No data available";
    }
    
    return "Data: " + nonZeroItems.map(item => 
      `${item.period}: ${item.tokens}`
    ).join(", ");
  };
  
  // Format tooltip for display
  const formatTooltip = (value: number, name: string) => {
    if (name === 'alternativeCost') return [`$${Number(value).toFixed(4)}`, 'Alternative Model Cost'];
    if (name === 'savings') return [`$${Number(value).toFixed(4)}`, 'Potential Savings'];
    return [value, name];
  };
  
  // Calculate tooltip label, using display_date when available
  const formatTooltipLabel = (label: string) => {
    // Find the data point that matches this label
    const dataPoint = data.find(item => item.period === label);
    
    // Add debug information to see what's being found or not found
    console.log(`Tooltip label: ${label}`);
    console.log(`Matching data point:`, dataPoint);
    
    // If we have a data point with a display_date, use it
    if (dataPoint?.display_date && dataPoint.display_date !== "Unknown Date") {
      return dataPoint.display_date;
    }
    
    // Fallback: try to format the label as a date
    if (label.includes(' ')) {
      // Check if it's in "Month Day" format (e.g., "May 15")
      const [month, day] = label.split(' ');
      if (['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].includes(month)) {
        const year = filters.to.getFullYear();
        return `${month} ${day}, ${year}`;
      }
    }
    
    // Return the label as a last resort
    return label;
  };
  
  // Show loading state
  if (loading) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold mb-2">Cost Optimization</h1>
        <OptimizationFilterBar />
        <div className="animate-pulse">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-24 bg-gray-100 rounded-md"></div>
            ))}
          </div>
          <div className="h-64 bg-gray-100 rounded-md mt-6"></div>
        </div>
      </div>
    );
  }
  
  // Show error state
  if (error) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold mb-2">Cost Optimization</h1>
        <OptimizationFilterBar />
        <div className="text-center py-6 text-red-500">
          <p>{error}</p>
        </div>
      </div>
    );
  }
  
  return (
    <div>
      <h1 className="text-2xl font-bold mb-2">Cost Optimization</h1>
      
      {/* Global Filter Bar */}
      <OptimizationFilterBar />
      
      {/* Overview section - styled like the Dashboard */}
      <div className="mt-8">
        <h2 className="text-xl font-semibold mb-4">Overview</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-gray-50 p-4 rounded-md">
            <h3 className="text-sm font-medium text-gray-500 mb-1">Current Cost</h3>
            <p className="text-2xl font-bold">{formatCurrency(totalActualCost)}</p>
            <p className="text-xs text-gray-500 mt-1">Using {data[0]?.actualModel || 'current models'}</p>
          </div>
          
          <div className="bg-gray-50 p-4 rounded-md">
            <h3 className="text-sm font-medium text-gray-500 mb-1">Potential Cost</h3>
            <p className="text-2xl font-bold">{formatCurrency(totalAlternativeCost)}</p>
            <p className="text-xs text-gray-500 mt-1">Using {data[0]?.alternativeModel || 'alternative models'}</p>
          </div>
          
          <div className="bg-gray-50 p-4 rounded-md">
            <h3 className="text-sm font-medium text-gray-500 mb-1">Potential Savings</h3>
            <p className="text-2xl font-bold text-green-600">{formatCurrency(totalSavings)}</p>
            <p className="text-xs text-gray-500 mt-1">~{averagePercentSavings.toFixed(1)}% less expensive</p>
          </div>
          
          <div className="bg-gray-50 p-4 rounded-md">
            <h3 className="text-sm font-medium text-gray-500 mb-1">Tokens</h3>
            <p className="text-2xl font-bold">{data.reduce((sum, item) => sum + item.tokens, 0).toLocaleString()}</p>
            <p className="text-xs text-gray-500 mt-1">Total usage</p>
          </div>
        </div>
      </div>
      
      {/* Usage Over Time Chart */}
      <div className="mt-8">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Usage Over Time</h2>
          <button 
            className="text-sm px-4 py-1 rounded border border-gray-300 hover:bg-gray-100"
            onClick={() => setShowSavings(!showSavings)}
          >
            {showSavings ? 'Hide Savings' : 'Show Savings'}
          </button>
        </div>
        
        <div>
          <p className="text-sm text-gray-500 mb-2">{getChartTitle()}</p>
          
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={data}
                margin={{ top: 10, right: 30, left: 20, bottom: 25 }}
                barSize={30}
              >
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis 
                  dataKey="period" 
                  tick={{ fontSize: 12 }}
                  height={40}
                  interval={
                    filters.interval === 'day' ? 3 : // Show every 4th hour
                    filters.interval === 'month' ? 2 : // Show every 3rd day
                    0 // Show all ticks for other intervals
                  }
                  tickMargin={8}
                  angle={filters.interval === 'month' ? -30 : 0}
                  textAnchor={filters.interval === 'month' ? 'end' : 'middle'}
                />
                <YAxis 
                  tickFormatter={formatYAxisValue}
                  width={60}
                  tick={{ fontSize: 12 }}
                />
                <Tooltip 
                  formatter={formatTooltip}
                  labelFormatter={formatTooltipLabel}
                />
                <Legend />
                <Bar 
                  dataKey="alternativeCost" 
                  name="Alternative Cost" 
                  stackId="a"
                  fill="#6366F1" 
                  radius={[4, 4, 0, 0]}
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
          
          <p className="text-xs text-gray-500 mt-2">{getDataSummary()}</p>
        </div>
      </div>
      
      {/* Cost Optimization Details - as a separate card like Model Distribution in dashboard */}
      <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <h2 className="text-xl font-semibold mb-4">Cost Optimization Details</h2>
          <div className="bg-white overflow-x-auto">
            <table className="min-w-full text-sm divide-y divide-gray-200">
              <thead>
                <tr className="text-left text-gray-500">
                  <th className="py-2">Period</th>
                  <th className="py-2">Current Model</th>
                  <th className="py-2 text-right">Current Cost</th>
                  <th className="py-2 text-right">Alternative Cost</th>
                  <th className="py-2 text-right">Savings</th>
                  <th className="py-2 text-right">Tokens</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {data.filter(row => row.tokens > 0).map((row, i) => (
                  <tr key={i} className="hover:bg-gray-50">
                    <td className="py-2">{row.period}</td>
                    <td className="py-2">{row.actualModel}</td>
                    <td className="py-2 text-right">{formatCurrency(row.actualCost)}</td>
                    <td className="py-2 text-right">{formatCurrency(row.alternativeCost)}</td>
                    <td className="py-2 text-right text-green-600">{formatCurrency(row.savings)}</td>
                    <td className="py-2 text-right">{row.tokens.toLocaleString()}</td>
                  </tr>
                ))}
                {/* Totals row */}
                <tr className="bg-gray-50 font-medium">
                  <td colSpan={2} className="py-2">Total</td>
                  <td className="py-2 text-right">{formatCurrency(totalActualCost)}</td>
                  <td className="py-2 text-right">{formatCurrency(totalAlternativeCost)}</td>
                  <td className="py-2 text-right text-green-600">{formatCurrency(totalSavings)}</td>
                  <td className="py-2 text-right">{data.reduce((sum, item) => sum + item.tokens, 0).toLocaleString()}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
        {/* Recommendation */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Recommendation</h2>
          <div className="bg-blue-50 p-4 rounded-md">
            {totalSavings > 0 ? (
              <p className="mb-4">
                Based on your usage patterns, switching from <span className="font-medium">{data[0]?.actualModel || 'current models'}</span> to <span className="font-medium">{data[0]?.alternativeModel || 'alternative models'}</span> for 
                certain tasks could reduce costs by approximately <span className="font-medium text-green-600">{averagePercentSavings.toFixed(1)}%</span>.
              </p>
            ) : (
              <p className="mb-4">
                {filters.model === 'claude-3-haiku' ? (
                  <>You're already using <span className="font-medium">claude-3-haiku</span>, which is currently the most cost-effective model in your pricing table.</>
                ) : (
                  <>No potential savings were found for the current selection. Try selecting a different model or time period.</>
                )}
              </p>
            )}
            <div className="flex gap-2">
              <button className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded text-sm">Apply Recommendation</button>
              <button className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded text-sm">Learn More</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CostOptimization; 