-- Database initialization script for AI Article Generation System
-- This script sets up the database schema and initial configuration

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create database user if not exists (handled by Docker compose)
-- The main tables will be created by SQLAlchemy/Alembic

-- Create indexes for better performance
-- These will be created via Alembic migrations

-- Initial configuration data
-- This will be populated by the application

-- Database is ready for SQLAlchemy models
