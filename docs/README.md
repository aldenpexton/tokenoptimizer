# Token Optimizer

A comprehensive dashboard for monitoring and optimizing LLM token usage across different models and endpoints.

## Documentation

All documentation can be found in the [docs](docs/) directory:

- [API Reference](docs/api-reference.md) - Complete API documentation
- [Frontend Guide](docs/frontend-guide.md) - Frontend development standards and practices
- [Requirements](docs/requirements.md) - Original requirements and specifications

## Features

- Real-time token usage monitoring
- Cost analysis and optimization recommendations
- Detailed usage logs with filtering and export
- Model performance comparisons
- Endpoint-specific analytics
- Historical trend analysis
- CSV export functionality

## Project Structure

```
tokenoptimizer/
├── backend/              # Flask backend application
├── frontend/             # React frontend application
├── sdk/                  # Client SDK for token logging
├── docs/                # Project documentation
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Setup

### Backend Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the development server:
```bash
cd backend
flask run --debug
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env.local
# Edit .env.local with your configuration
```

3. Run the development server:
```bash
npm run dev
```

## Development

### Backend Development

The backend is built with Flask and uses:
- Supabase for data storage
- SQLAlchemy for ORM
- Flask-CORS for cross-origin support
- Pandas for data analysis
- PyTest for testing

Key files:
- `backend/app.py` - Main application entry point
- `backend/routes/` - API route definitions
- `backend/services/` - Business logic
- `backend/models/` - Database models
- `backend/tests/` - Test suite

### Frontend Development

The frontend is built with React and uses:
- TypeScript for type safety
- React Query for data fetching
- TailwindCSS for styling
- Recharts for visualizations
- React Testing Library for testing

See [Frontend Guide](docs/frontend-guide.md) for detailed best practices and component documentation.

## Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

## Deployment

### Backend Deployment

1. Build the Docker image:
```bash
docker build -t tokenoptimizer-backend ./backend
```

2. Run the container:
```bash
docker run -p 5002:5002 tokenoptimizer-backend
```

### Frontend Deployment

1. Build the production bundle:
```bash
cd frontend
npm run build
```

2. The built files will be in the `dist` directory, ready to be served by a static file server.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please check our [documentation](docs/) or open an issue in the repository. 