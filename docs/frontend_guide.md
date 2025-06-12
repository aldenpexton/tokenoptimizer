# Frontend Development Guide

## Tech Stack

- React 18+
- TypeScript
- TailwindCSS for styling
- React Query for API data fetching and caching
- React Router for navigation
- Recharts for data visualization

## Project Structure

```
frontend/
├── src/
│   ├── components/        # Reusable UI components (PascalCase files)
│   ├── features/          # Domain-specific component groups (e.g. Dashboard, Logs)
│   ├── hooks/             # Custom React hooks (camelCase files)
│   ├── api/               # API integration layer
│   ├── types/             # TypeScript type definitions
│   ├── utils/             # Utility functions (camelCase files)
│   └── pages/             # Route-level components (e.g. LogsPage, DashboardPage)
```

## Aesthetic and Visual Style Guidelines

- **Overall Style**: Simple, clean, and professional — inspired by Stripe’s UI.
- **Layout**: Use consistent padding (`p-4`, `p-6`), large spacing between cards (`gap-6`, `mb-8`), and grid-based alignment.
- **Colors**: Stick to Tailwind’s neutral color palette. Use `gray-100`/`white` backgrounds, `gray-700` for text, and `blue-500` for interactive elements.
- **Typography**: Use Tailwind's default `font-sans`. Headings should be `text-xl` or `text-2xl`, labels `text-sm`, and body text `text-base`.
- **Cards**: Apply soft shadows (`shadow-sm`, `hover:shadow-md`), large rounded corners (`rounded-2xl`), and subtle hover effects.
- **Charts**: Minimalist — thin lines, no grid by default. Use tooltips and legends sparingly. Keep fonts consistent with the rest of the UI.
- **Tables and Logs**: Clean lines, alternating row colors (`even:bg-gray-50`), sticky headers where possible.
- **Buttons and Inputs**: Rounded corners, soft shadows, subtle hover states. Prioritize accessibility with clear focus rings.

## Component Best Practices

### 1. Component Organization

- Use functional components with TypeScript
- Keep components focused and single-responsibility
- Extract reusable logic into custom hooks
- Use proper TypeScript types for props and state
- Use PascalCase file naming for components

Example:

```typescript
interface MetricsCardProps {
  title: string;
  value: number;
  change?: number;
  loading?: boolean;
}

export const MetricsCard: React.FC<MetricsCardProps> = ({
  title,
  value,
  change,
  loading = false,
}) => {
  if (loading) return <LoadingSkeleton data-testid="loading-skeleton" />;

  return (
    <div className="metrics-card">
      <h3 className="metrics-title">{title}</h3>
      <div className="mt-2 flex items-end gap-2">
        <span className="text-2xl font-semibold">{value.toLocaleString()}</span>
        {change && <ChangeIndicator value={change} />}
      </div>
    </div>
  );
};
```

### 2. Data Fetching

- Use React Query for all API calls
- Implement proper error handling and loading states
- Cache responses appropriately
- Type all API responses

Example:

```typescript
export const useMetricsSummary = (filters: FilterParams) => {
  return useQuery({
    queryKey: ['metrics', 'summary', filters],
    queryFn: () => fetchMetricsSummary(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};
```

### 3. API Error Handling

- Catch and handle server errors gracefully

Example:

```typescript
try {
  const response = await fetchData();
  return response.data;
} catch (error) {
  if (axios.isAxiosError(error) && error.response?.status === 401) {
    // Redirect or show token error
  }
  throw error;
}
```

### 4. State Management

- Use React Query for server state
- Use Context API or Zustand for global UI state
- Keep local state minimal

### 5. Routing Patterns

- Define routes clearly and co-locate related page components

Example:

```tsx
<Routes>
  <Route path="/" element={<DashboardPage />} />
  <Route path="/logs" element={<LogsPage />} />
</Routes>
```

### 6. Styling Guidelines

- Use Tailwind utility classes
- Create reusable component styles with @apply
- Use consistent spacing, typography, and color schemes

Example:

```css
@layer components {
  .metrics-card {
    @apply p-4 rounded-lg bg-white shadow-sm hover:shadow-md transition-shadow;
  }

  .metrics-title {
    @apply text-gray-600 text-sm font-medium;
  }
}
```

### 7. Performance Optimization

- Memoize computed values and callbacks with `useMemo` and `useCallback`
- Use `React.memo` for heavy components
- Lazy-load routes and large charts
- Use proper key props in lists

Example:

```typescript
const MemoizedChart = React.memo(({ data }) => (
  <ResponsiveContainer width="100%" height={300}>
    <LineChart data={data}>
      {/* Chart config */}
    </LineChart>
  </ResponsiveContainer>
));
```

### 8. Error Handling

- Implement error boundaries
- Show user-friendly messages
- Log errors appropriately
- Provide retry buttons

Example:

```tsx
import { ErrorBoundary as FallbackErrorBoundary } from 'react-error-boundary';

export const ErrorBoundary: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <FallbackErrorBoundary
      fallbackRender={({ error, resetErrorBoundary }) => (
        <div className="p-4 bg-red-50 text-red-700 rounded">
          <h3>Something went wrong</h3>
          <pre>{error.message}</pre>
          <button onClick={resetErrorBoundary}>Try again</button>
        </div>
      )}
    >
      {children}
    </FallbackErrorBoundary>
  );
};
```

### 9. Forms and Inputs

- Use `react-hook-form` for controlled forms
- Implement validation and default values
- Support date pickers and multi-select dropdowns

### 10. Common Components

- Metrics cards
- Charts and graphs
- Paginated, sortable tables
- Filter dropdowns
- Layouts (nav, page wrapper)
- Toasts and modals

## API Integration

- Follow `/API.md` for endpoint definitions
- Type all response objects
- Handle all documented error states
- Use caching/staleTime where applicable

## Deployment

- Use `.env.local` for environment variables
- Optimize with `npm run build`
- Enable error tracking (e.g., Sentry)
- Setup performance monitoring if needed

## Development Workflow

1. Create feature branch from `main`
2. Implement feature with comments and tests
3. Run linter and type checker
4. Open a pull request
5. Request code review
6. Merge to `main`
7. Write changelog if applicable
8. Tag PR with related issue or feature

