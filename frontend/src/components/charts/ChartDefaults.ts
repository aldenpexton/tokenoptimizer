// Chart default styles and helper functions
export const chartDefaults = {
  // Simple, clean chart theme
  theme: {
    colors: ['#635bff', '#24b47e', '#f7b84b', '#cd3d64'],
    backgroundColor: '#ffffff',
  },
  
  // Common props for all charts
  commonProps: {
    margin: { top: 10, right: 30, left: 0, bottom: 0 },
    style: {
      fontSize: '12px',
      fontFamily: '-apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    },
  },
  
  // Responsive container props
  containerProps: {
    width: '100%',
    height: 300,
  },
  
  // Tooltip styles
  tooltipStyle: {
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    border: '1px solid #e5e9f0',
    borderRadius: '4px',
    boxShadow: '0 2px 5px -1px rgba(50,50,93,.25)',
    padding: '8px 12px',
    color: '#1a2c42',
  },
} as const;

// Helper function to format currency values
export const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
  }).format(value);
};

// Helper function to format large numbers
export const formatNumber = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    notation: 'compact',
    compactDisplay: 'short',
  }).format(value);
}; 