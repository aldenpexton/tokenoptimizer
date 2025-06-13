interface Config {
  apiUrl: string;
  env: string;
  frontendPort: number;
}

const devConfig: Config = {
  apiUrl: 'http://localhost:5002',
  env: 'development',
  frontendPort: 3002
};

const prodConfig: Config = {
  apiUrl: process.env.REACT_APP_API_URL || 'https://tokenoptimizer.onrender.com',
  env: 'production',
  frontendPort: 3002
};

const config: Config = process.env.NODE_ENV === 'production' ? prodConfig : devConfig;

export default config; 