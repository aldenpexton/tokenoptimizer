interface Config {
  apiUrl: string;
  env: string;
  frontendPort: number;
}

const developmentConfig: Config = {
  apiUrl: 'http://localhost:5002',
  env: 'development',
  frontendPort: 3002
};

const productionConfig: Config = {
  apiUrl: process.env.REACT_APP_API_URL || 'https://your-render-service.onrender.com',
  env: 'production',
  frontendPort: 3002
};

const config: Config = process.env.NODE_ENV === 'production' ? productionConfig : developmentConfig;

export default config; 