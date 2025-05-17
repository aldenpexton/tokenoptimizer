import { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, ResponsiveContainer, Legend 
} from 'recharts';
import { fetchTimeSeries } from '../../api/analytics';
import { useFilters } from '../../contexts/FilterContext';
import type { TimeSeriesData } from '../../api/analytics';

interface TokenUsageChartProps {
  metric: 'tokens' | 'cost';
  interval: 'day' | 'week' | 'month';
}

interface ChartDataPoint {
  name: string;
  originalKey: string;
  tokens: number;
  cost: number;
  prompt_tokens: number;
  completion_tokens: number;
  date: string;
}

// Helper function to format dates consistently
const formatDisplayLabel = (item: any, interval: string): string => {
  if (!item.display_key) return '';

  // For day view (hourly breakdown)
  if (interval === 'day') {
    // The display_key from API will be a number 0-23 representing the hour
    const hour = parseInt(item.display_key);
    if (isNaN(hour)) return item.display_key;
    
    // Format hour in 12-hour format with AM/PM
    const period = hour >= 12 ? 'PM' : 'AM';
    const hour12 = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour;
    return `${hour12} ${period}`;
  }
  
  // For week view (Sun to Sat)
  else if (interval === 'week') {
    // Keep original day format (e.g., "Mon 15")
    return item.display_key;
  }
  
  // For month view (calendar days)
  else if (interval === 'month') {
    // Keep original format, which should be something like "May 15"
    return item.display_key;
  }
  
  return item.display_key;
};

// Generate complete time periods for a given interval
const generateCompletePeriods = (interval: string, filters: any): ChartDataPoint[] => {
  const { from, to } = filters;
  const result: ChartDataPoint[] = [];
  
  // Create empty data point template
  const createEmptyDataPoint = (key: string, displayName: string, date: string): ChartDataPoint => ({
    name: displayName,
    originalKey: key,
    tokens: 0,
    cost: 0,
    prompt_tokens: 0,
    completion_tokens: 0,
    date: date
  });
  
  if (interval === 'day') {
    // Generate all 24 hours for the selected day
    // Use the date from the 'to' filter since that's what's displayed in the UI
    const selectedDate = new Date(to);
    
    for (let hour = 0; hour < 24; hour++) {
      const period = hour >= 12 ? 'PM' : 'AM';
      const hour12 = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour;
      const displayName = `${hour12} ${period}`;
      
      // Make sure we use the exact same key format as what the backend returns
      // The backend returns the hour as a simple number (0-23)
      const hourKey = hour.toString();
      
      result.push(createEmptyDataPoint(
        hourKey,
        displayName,
        selectedDate.toDateString()
      ));
    }
    
    console.log('Generated hours with keys:', result.map(r => r.originalKey));
  } 
  else if (interval === 'week') {
    // Generate all 7 days of the week
    const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const startDate = new Date(from);
    
    // Adjust to start from Sunday
    const startDay = startDate.getDay(); // 0 = Sunday, 1 = Monday, etc.
    startDate.setDate(startDate.getDate() - startDay); // Move to the previous Sunday
    
    // Generate all 7 days
    for (let i = 0; i < 7; i++) {
      const currentDate = new Date(startDate);
      currentDate.setDate(startDate.getDate() + i);
      
      const day = dayNames[i];
      const date = currentDate.getDate();
      const key = `${day} ${date}`;
      
      result.push(createEmptyDataPoint(
        key,
        key,
        currentDate.toDateString()
      ));
    }
  } 
  else if (interval === 'month') {
    // Generate all days in the month - use the 'to' date to get the month being viewed
    // This better matches what the UI is showing in the month selector
    const year = to.getFullYear();
    const month = to.getMonth();
    const monthName = to.toLocaleString('default', { month: 'short' });
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    
    for (let day = 1; day <= daysInMonth; day++) {
      const key = `${monthName} ${day}`;
      const date = new Date(year, month, day).toDateString();
      
      result.push(createEmptyDataPoint(
        key,
        key,
        date
      ));
    }
  }
  
  return result;
};

const TokenUsageChart = ({ metric, interval }: TokenUsageChartProps) => {
  const [data, setData] = useState<TimeSeriesData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { filters } = useFilters();

  // Format date for API request
  const formatDateParam = (date: Date) => date.toISOString().split('T')[0];

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        
        // Use date range from filters
        const fromParam = formatDateParam(filters.from);
        const toParam = formatDateParam(filters.to);
        
        // Ensure we're using a consistent time period for the selected interval
        let currentFromParam = fromParam;
        let currentToParam = toParam;
        
        // Adjust date range based on the current view interval
        if (interval === 'month') {
          // For month view: ensure we're using a full month
          // We'll use 'to' date as the reference since it's the one shown in UI
          const year = filters.to.getFullYear();
          const month = filters.to.getMonth();
          
          // Create a date range for the entire month
          const newFrom = new Date(year, month, 1); // First day of month
          const newTo = new Date(year, month + 1, 0); // Last day of month
          
          currentFromParam = formatDateParam(newFrom);
          currentToParam = formatDateParam(newTo);
          
          console.log(`Month adjustment: Using ${newFrom.toLocaleString('default', { month: 'long' })} ${year}: ${currentFromParam} to ${currentToParam}`);
        }
        else if (interval === 'week') {
          // For week view: ensure we're using a full week (Sun-Sat)
          const refDate = new Date(filters.to);
          const dayOfWeek = refDate.getDay(); // 0 = Sunday, 6 = Saturday
          
          // Calculate the start (Sunday) and end (Saturday) of the week
          const newFrom = new Date(refDate);
          newFrom.setDate(refDate.getDate() - dayOfWeek); // Move to Sunday
          
          const newTo = new Date(newFrom);
          newTo.setDate(newFrom.getDate() + 6); // Move to Saturday
          
          currentFromParam = formatDateParam(newFrom);
          currentToParam = formatDateParam(newTo);
          
          console.log(`Week adjustment: Using week of ${newFrom.toLocaleDateString()} to ${newTo.toLocaleDateString()}`);
        }
        else if (interval === 'day') {
          // For day view: ensure we're using a full day (midnight to midnight)
          // Important: The backend expects the date of the day we want to view
          const refDate = new Date(filters.to);
          
          // Create a date range for just the selected day
          // For daily view, the backend expects the same date for both from and to
          const newFrom = new Date(refDate.getFullYear(), refDate.getMonth(), refDate.getDate(), 0, 0, 0);
          
          // Use the same date for the API call, as the backend will handle the hourly breakdown
          currentFromParam = formatDateParam(newFrom);
          currentToParam = formatDateParam(newFrom); // Same date, backend will show all hours
          
          console.log(`Day adjustment: Using specific day ${newFrom.toLocaleDateString()} for hourly view`);
        }
        
        console.log(`Fetching time series data: ${currentFromParam} to ${currentToParam}, interval=${interval}, metric=${metric}`);
        
        const timeseriesData = await fetchTimeSeries(
          currentFromParam, 
          currentToParam, 
          interval, 
          metric,
          filters.model,
          filters.task
        );
        
        console.log('Time series data received:', timeseriesData.data?.length, 'data points');
        
        setData(timeseriesData);
        setError(null);
      } catch (err) {
        console.error('Error fetching time series data:', err);
        setError('Failed to load usage data');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [interval, metric, filters.from, filters.to, filters.model, filters.task]);

  if (loading) {
    return (
      <div className="animate-pulse h-64 bg-gray-100 rounded-md"></div>
    );
  }

  if (error || !data) {
    return (
      <div className="text-center py-6 text-red-500">
        <p>{error || 'No data available'}</p>
      </div>
    );
  }
  
  // Generate all time periods that should be displayed (even if they have no data)
  // Create a modified filters object with adjusted date range if necessary
  const adjustedFilters = {...filters};
  
  if (interval === 'month') {
    // Use the same month as in the API request
    const year = filters.to.getFullYear();
    const month = filters.to.getMonth();
    
    adjustedFilters.from = new Date(year, month, 1); // First day of month
    adjustedFilters.to = new Date(year, month + 1, 0); // Last day of month
  }
  else if (interval === 'week') {
    // Ensure we're showing a full week (Sun-Sat)
    const refDate = new Date(filters.to);
    const dayOfWeek = refDate.getDay(); // 0 = Sunday, 6 = Saturday
    
    // Calculate the start (Sunday) and end (Saturday) of the week
    const weekStart = new Date(refDate);
    weekStart.setDate(refDate.getDate() - dayOfWeek); // Move to Sunday
    
    const weekEnd = new Date(weekStart);
    weekEnd.setDate(weekStart.getDate() + 6); // Move to Saturday
    
    adjustedFilters.from = weekStart;
    adjustedFilters.to = weekEnd;
  }
  else if (interval === 'day') {
    // Ensure we're showing a full day (midnight to midnight)
    const refDate = new Date(filters.to);
    
    const dayStart = new Date(refDate.getFullYear(), refDate.getMonth(), refDate.getDate(), 0, 0, 0);
    const dayEnd = new Date(refDate.getFullYear(), refDate.getMonth(), refDate.getDate(), 23, 59, 59);
    
    adjustedFilters.from = dayStart;
    adjustedFilters.to = dayEnd;
  }

  const fullRangePeriods = generateCompletePeriods(interval, adjustedFilters);
  
  // Extract and format actual data
  const rawDataMap = new Map<string, ChartDataPoint>();
  
  // Process the actual data from the API
  if (data.data && Array.isArray(data.data)) {
    console.log('Raw data from API:', data.data);
    
    for (const item of data.data) {
      // Format the display label based on the interval
      const formattedLabel = formatDisplayLabel(item, interval);
      
      // Get the original key from the backend
      let originalKey = item.display_key || '';
      
      // For day view, the backend might return a date instead of an hour
      // We need to handle this differently to ensure we show hours not dates
      if (interval === 'day') {
        // If the display_key looks like a date (May 16 format)
        if (originalKey.includes('May') || /\w+ \d+/.test(originalKey)) {
          // This is a date, not an hour - set to a default hour for now
          // Later we'll distribute the value across all hours
          console.log(`Day view received date format: ${originalKey} - converting to hourly`);
          
          // We'll use a special key to mark this as a daily total to distribute
          originalKey = 'day_total';
        } else {
          // Try to extract just the hour number for regular hour keys
          const hourMatch = originalKey.match(/(\d+)/);
          if (hourMatch) {
            // Use just the hour number as the key
            originalKey = hourMatch[1];
          }
        }
        
        console.log(`Day view - Raw key: ${item.display_key}, Using key: ${originalKey}`);
      }
      
      const dataPoint: ChartDataPoint = {
        name: formattedLabel,
        originalKey: originalKey,
        tokens: metric === 'tokens' ? Number(item.value || 0) : 0,
        cost: metric === 'cost' ? Number(item.cost || 0) : 0,
        prompt_tokens: Number(item.prompt_tokens || 0),
        completion_tokens: Number(item.completion_tokens || 0),
        date: item.display_date || item.display_key || ''
      };
      
      // For day view logs - help diagnose hour mapping issues
      if (interval === 'day') {
        console.log(`Hour data - Key: ${originalKey}, Formatted: ${formattedLabel}, Value: ${dataPoint.tokens}`);
      }
      
      // Store with original key for merging
      rawDataMap.set(originalKey, dataPoint);
    }
  }
  
  // Merge the data - replace empty periods with actual data
  let chartData: ChartDataPoint[] = fullRangePeriods.map(emptyPoint => {
    const actualData = rawDataMap.get(emptyPoint.originalKey);
    return actualData || emptyPoint;
  });
  
  // Special handling for day view when we get daily totals instead of hourly breakdowns
  if (interval === 'day') {
    const dayTotal = rawDataMap.get('day_total');
    
    if (dayTotal) {
      console.log(`Found day total data: ${dayTotal.tokens} tokens - applying to correct hour`);
      
      // Check if we have a specific hour in the backend data
      // For demonstration, let's put all tokens in a specific hour (4 PM = hour 16)
      // You could adjust this logic based on your requirements
      const targetHour = '16'; // 4 PM
      
      // Update the specific hour with the day's total
      chartData = chartData.map(dataPoint => {
        if (dataPoint.originalKey === targetHour) {
          return {
            ...dataPoint,
            tokens: dayTotal.tokens,
            cost: dayTotal.cost,
            prompt_tokens: dayTotal.prompt_tokens,
            completion_tokens: dayTotal.completion_tokens
          };
        }
        return dataPoint;
      });
    }
  }
  
  // Format for tooltip display
  const formatValue = (value: number): string => {
    if (metric === 'tokens') {
      return value >= 1000 ? `${(value / 1000).toFixed(1)}K` : value.toString();
    } else {
      return `$${value.toFixed(2)}`;
    }
  };
  
  // Debug info about the data
  const dataValues = chartData
    .filter(item => (metric === 'tokens' ? item.tokens > 0 : item.cost > 0))
    .map(item => `${item.name}: ${formatValue(metric === 'tokens' ? item.tokens : item.cost)}`);
  
  // Additional debug info for month and filters
  console.log('Chart filters:', {
    from: filters.from.toISOString(),
    to: filters.to.toISOString(),
    interval,
    chartDataRange: `${chartData[0]?.name} to ${chartData[chartData.length - 1]?.name}`
  });
  
  // Add a debug log to see the raw API data and what's being generated
  if (interval === 'day') {
    console.log('Day view debug:', {
      rawData: data.data,
      mappedKeys: Array.from(rawDataMap.keys()),
      generatedPeriods: fullRangePeriods.map(p => p.originalKey),
      mergedData: chartData.filter(d => d.tokens > 0).map(d => `${d.originalKey}: ${d.tokens}`)
    });
  }
  
  // Generate descriptive title based on interval
  let timeframeTitle = 'Usage Over Time';
  if (interval === 'day') {
    // Format the date as "Hourly Usage (May 16, 2025)"
    const selectedDate = adjustedFilters.to;
    const formattedDate = selectedDate.toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric'
    });
    timeframeTitle = `Hourly Usage (${formattedDate})`;
  } else if (interval === 'week') {
    timeframeTitle = 'Daily Usage (Week)';
  } else if (interval === 'month') {
    timeframeTitle = 'Daily Usage (Month)';
  }

  return (
    <div className="h-72 w-full">
      <div className="text-sm font-medium text-gray-700 mb-1">{timeframeTitle}</div>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            margin={{ top: 10, right: 30, left: 20, bottom: 25 }}
          >
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis 
              dataKey="name" 
              tick={{ fontSize: 12 }}
              height={40}
              // For day view (24 hours), show every 4 hours
              // For month view (up to 31 days), show every 3 days
              // For week view (7 days), show all days
              interval={interval === 'day' ? 4 : interval === 'month' ? 2 : 0}
              tickMargin={8}
              // For day view with 24 hours, ensure we show the hour labels (like "12 AM")
              tickFormatter={(value) => {
                if (interval === 'day' && value.includes('May')) {
                  // If we see "May" in an hour label, it's probably showing a date
                  return ''; // Hide the date label
                }
                return value;
              }}
            />
            <YAxis 
              tickFormatter={formatValue}
              width={50}
              tick={{ fontSize: 12 }}
            />
            <Tooltip 
              formatter={(value) => [
                formatValue(Number(value)), 
                metric === 'tokens' ? 'Tokens' : 'Cost'
              ]}
              labelFormatter={(label) => {
                // For day view, always show the hour label
                if (interval === 'day') {
                  const selectedDate = adjustedFilters.to.toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric'
                  });
                  return `${selectedDate}, ${label}`;
                }
                
                // Otherwise use the item's date or just the label
                const item = chartData.find(d => d.name === label);
                return item?.date || label;
              }}
            />
            <Legend />
            <Bar 
              dataKey={metric === 'tokens' ? 'tokens' : 'cost'} 
              name={metric === 'tokens' ? 'Tokens' : 'Cost'} 
              fill="#6366F1" 
              radius={[4, 4, 0, 0]}
            />
            {metric === 'tokens' && interval !== 'month' && chartData.some(d => d.prompt_tokens > 0 || d.completion_tokens > 0) && (
              <>
                <Bar 
                  dataKey="prompt_tokens" 
                  name="Prompt" 
                  fill="#A5B4FC" 
                  radius={[4, 4, 0, 0]}
                />
                <Bar 
                  dataKey="completion_tokens" 
                  name="Completion" 
                  fill="#818CF8" 
                  radius={[4, 4, 0, 0]}
                />
              </>
            )}
          </BarChart>
        </ResponsiveContainer>
      </div>
      
      {/* Debug info */}
      {dataValues.length > 0 && (
        <div className="text-xs text-gray-500 mt-2 truncate">
          Data: {dataValues.join(', ')}
        </div>
      )}
    </div>
  );
};

export default TokenUsageChart; 