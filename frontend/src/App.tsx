import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import CostOptimization from './pages/CostOptimization';
import Layout from './components/Layout';
import { FilterProvider } from './contexts/FilterContext';

function App() {
  return (
    <FilterProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="optimization" element={<CostOptimization />} />
            {/* Add more routes as needed */}
          </Route>
        </Routes>
      </Router>
    </FilterProvider>
  );
}

export default App;
