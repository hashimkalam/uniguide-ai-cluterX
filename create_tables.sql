-- SQL commands to create tables in PostgreSQL
-- Run these in your local PostgreSQL database

-- Create universities table
CREATE TABLE universities (
    id SERIAL PRIMARY KEY,
    pubukprn VARCHAR UNIQUE NOT NULL,
    ukprn VARCHAR,
    legal_name VARCHAR NOT NULL,
    first_trading_name VARCHAR,
    other_names TEXT,
    address TEXT,
    telephone VARCHAR,
    website VARCHAR,
    country VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create courses table
CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    kiscourseid VARCHAR UNIQUE NOT NULL,
    pubukprn VARCHAR NOT NULL REFERENCES universities(pubukprn),
    title VARCHAR NOT NULL,
    title_welsh VARCHAR,
    kis_mode VARCHAR,
    kis_level VARCHAR,
    hecos_code VARCHAR,
    ucas_prog_id VARCHAR,
    honours BOOLEAN,
    foundation BOOLEAN,
    sandwich BOOLEAN,
    year_abroad BOOLEAN,
    nhs BOOLEAN,
    distance_learning BOOLEAN,
    num_stage INTEGER,
    location_change BOOLEAN,
    kisaaim_code VARCHAR,
    year INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create entry_requirements table
CREATE TABLE entry_requirements (
    id SERIAL PRIMARY KEY,
    kiscourseid VARCHAR NOT NULL REFERENCES courses(kiscourseid),
    kis_mode VARCHAR,
    tariff_unavail_reason VARCHAR,
    tariff_population VARCHAR,
    tariff_agg FLOAT,
    tariff_agg_year INTEGER,
    tariff_year1 FLOAT,
    tariff_year2 FLOAT,
    tariff_subject VARCHAR,
    t001_t048 FLOAT,
    t048_t064 FLOAT,
    t064_t080 FLOAT,
    t080_t096 FLOAT,
    t096_t112 FLOAT,
    t112_t128 FLOAT,
    t128_t144 FLOAT,
    t144_t160 FLOAT,
    t160_t176 FLOAT,
    t176_t192 FLOAT,
    t192_t208 FLOAT,
    t208_t224 FLOAT,
    t224_t240 FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_universities_pubukprn ON universities(pubukprn);
CREATE INDEX idx_courses_kiscourseid ON courses(kiscourseid);
CREATE INDEX idx_courses_pubukprn ON courses(pubukprn);
CREATE INDEX idx_entry_requirements_kiscourseid ON entry_requirements(kiscourseid);