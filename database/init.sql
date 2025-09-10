-- Database initialization for Travel Planner Phase 2
-- This script creates the initial tables and indexes

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

-- User preferences table
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    origin_city VARCHAR(255),
    preferred_budget INTEGER DEFAULT 1500,
    favorite_interests TEXT[], -- Array of interests
    notification_settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trips table
CREATE TABLE trips (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    destination VARCHAR(255) NOT NULL,
    origin_city VARCHAR(255) NOT NULL,
    days INTEGER NOT NULL,
    month VARCHAR(50) NOT NULL,
    budget_total DECIMAL(10,2) NOT NULL,
    interests TEXT[] NOT NULL,
    visa_passport VARCHAR(100),
    preferred_destination VARCHAR(255),
    trip_data JSONB NOT NULL, -- Complete trip plan from AI
    status VARCHAR(50) DEFAULT 'completed',
    is_favorite BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Feedback table
CREATE TABLE feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    aspects TEXT[], -- What they liked
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User sessions table (for JWT token management)
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_agent TEXT,
    ip_address INET
);

-- Indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_trips_user_id ON trips(user_id);
CREATE INDEX idx_trips_created_at ON trips(created_at DESC);
CREATE INDEX idx_feedback_trip_id ON feedback(trip_id);
CREATE INDEX idx_feedback_user_id ON feedback(user_id);
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for auto-updating updated_at
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at 
    BEFORE UPDATE ON user_preferences 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_trips_updated_at 
    BEFORE UPDATE ON trips 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for testing (optional)
INSERT INTO users (email, name, password_hash) VALUES 
('demo@example.com', 'Demo User', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewsqyxoJ5DXBpHpS'); -- password: "demo123"

-- Sample user preferences
INSERT INTO user_preferences (user_id, origin_city, preferred_budget, favorite_interests) 
SELECT id, 'Hyderabad', 1500, ARRAY['culture', 'food'] 
FROM users WHERE email = 'demo@example.com';

-- Sample trip (if you want test data)
-- This will be populated by the application

-- Grant permissions to travel_user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO travel_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO travel_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO travel_user;
