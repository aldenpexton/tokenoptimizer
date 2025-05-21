-- Update model_alternatives table to simplify structure

-- First, let's create a backup of the existing table
CREATE TABLE model_alternatives_backup AS SELECT * FROM model_alternatives;

-- Now, update the model_alternatives table by recreating it
DROP TABLE IF EXISTS model_alternatives;

CREATE TABLE model_alternatives (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_model TEXT NOT NULL REFERENCES model_pricing(model),
    alternative_model TEXT NOT NULL REFERENCES model_pricing(model),
    similarity_score NUMERIC(3, 2) NOT NULL, -- Quality score between 0.0-1.0
    is_recommended BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster lookups
CREATE INDEX idx_model_alternatives_source ON model_alternatives(source_model);

-- Add back the trigger for updated_at
CREATE TRIGGER update_model_alternatives_updated_at
BEFORE UPDATE ON model_alternatives
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Populate with data from backup (without the notes field)
INSERT INTO model_alternatives 
(source_model, alternative_model, similarity_score, is_recommended)
SELECT 
    source_model,
    alternative_model,
    similarity_score,
    is_recommended
FROM model_alternatives_backup
WHERE source_model IN (SELECT model FROM model_pricing)
  AND alternative_model IN (SELECT model FROM model_pricing);

-- Sample data to ensure common models have alternatives
INSERT INTO model_alternatives 
(source_model, alternative_model, similarity_score, is_recommended)
VALUES
('claude-3-opus', 'claude-3-haiku', 0.75, TRUE),
('claude-3-sonnet', 'claude-3-haiku', 0.85, TRUE),
('gpt-4', 'gpt-3.5-turbo', 0.75, TRUE),
('gpt-4', 'claude-3-haiku', 0.82, TRUE),
('claude-3-opus', 'claude-3-sonnet', 0.90, TRUE),
('mistral-large', 'mistral-medium', 0.87, TRUE),
('mistral-medium', 'mistral-small', 0.80, TRUE)
ON CONFLICT (id) DO NOTHING; 