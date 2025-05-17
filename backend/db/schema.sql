-- TokenOptimizer Database Schema

-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Token usage logs table
CREATE TABLE token_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    model TEXT NOT NULL,
    endpoint_name TEXT DEFAULT 'default',
    prompt_tokens INTEGER NOT NULL,
    completion_tokens INTEGER NOT NULL,
    total_tokens INTEGER NOT NULL,
    latency_ms INTEGER NOT NULL,
    input_cost NUMERIC(10, 6) NOT NULL,
    output_cost NUMERIC(10, 6) NOT NULL,
    total_cost NUMERIC(10, 6) NOT NULL,
    api_provider TEXT NOT NULL, -- OpenAI, Anthropic, Mistral, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for faster queries
CREATE INDEX idx_token_logs_timestamp ON token_logs(timestamp);
CREATE INDEX idx_token_logs_endpoint_name ON token_logs(endpoint_name);
CREATE INDEX idx_token_logs_model ON token_logs(model);

-- Model pricing table
CREATE TABLE model_pricing (
    model TEXT PRIMARY KEY,
    input_price NUMERIC(10, 6) NOT NULL, -- Price per 1K input tokens
    output_price NUMERIC(10, 6) NOT NULL, -- Price per 1K output tokens
    api_provider TEXT NOT NULL, -- OpenAI, Anthropic, Mistral, etc.
    is_active BOOLEAN DEFAULT TRUE,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Model alternatives table for cost comparison
CREATE TABLE model_alternatives (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_model TEXT NOT NULL REFERENCES model_pricing(model),
    alternative_model TEXT NOT NULL REFERENCES model_pricing(model),
    similarity_score NUMERIC(3, 2) NOT NULL, -- How similar the models are (0.0-1.0)
    is_recommended BOOLEAN DEFAULT TRUE, -- Flag for preferred recommendations
    notes TEXT, -- Optional explanation of comparison
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster lookups
CREATE INDEX idx_model_alternatives_source ON model_alternatives(source_model);

-- Add some example pricing data
INSERT INTO model_pricing (model, input_price, output_price, api_provider) VALUES
('gpt-3.5-turbo', 0.0005, 0.0015, 'OpenAI'),
('gpt-4', 0.03, 0.06, 'OpenAI'),
('claude-3-opus', 0.015, 0.075, 'Anthropic'),
('claude-3-sonnet', 0.003, 0.015, 'Anthropic'),
('claude-3-haiku', 0.00025, 0.00125, 'Anthropic'),
('mistral-small', 0.002, 0.006, 'Mistral'),
('mistral-medium', 0.006, 0.018, 'Mistral'),
('mistral-large', 0.08, 0.24, 'Mistral');

-- Add example model alternatives for cost comparison
INSERT INTO model_alternatives (source_model, alternative_model, similarity_score, notes) VALUES
('gpt-4', 'gpt-3.5-turbo', 0.75, 'Good for most general tasks with significant cost savings'),
('claude-3-opus', 'claude-3-sonnet', 0.85, 'Excellent alternative with minimal quality difference'),
('claude-3-sonnet', 'claude-3-haiku', 0.70, 'Good for simple tasks and high throughput needs'),
('mistral-large', 'mistral-medium', 0.80, 'Substantial cost savings with good performance'),
('claude-3-opus', 'claude-3-haiku', 0.60, 'Maximum cost savings for simpler tasks');

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for token_logs
CREATE TRIGGER update_token_logs_updated_at
BEFORE UPDATE ON token_logs
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Create trigger for model_pricing
CREATE TRIGGER update_model_pricing_updated_at
BEFORE UPDATE ON model_pricing
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Create trigger for model_alternatives
CREATE TRIGGER update_model_alternatives_updated_at
BEFORE UPDATE ON model_alternatives
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column(); 