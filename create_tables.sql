-- ADC Manufacturing Database Schema
-- Run this against the adc_manufacturing database
-- Requires schemas: manufacturing, analytical, quality

-- ─── MANUFACTURING SCHEMA ────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS manufacturing.batches (
    batch_number        VARCHAR(20) PRIMARY KEY,
    product             VARCHAR(50) NOT NULL,
    manufacturing_date  DATE NOT NULL,
    batch_size_mg       NUMERIC(10,1),
    overall_yield_mg    NUMERIC(10,1),
    batch_status        VARCHAR(10) CHECK (batch_status IN ('Pass', 'Fail'))
);

CREATE TABLE IF NOT EXISTS manufacturing.bioconjugation (
    id                      SERIAL PRIMARY KEY,
    batch_number            VARCHAR(20) REFERENCES manufacturing.batches(batch_number),
    reaction_temperature_c  NUMERIC(5,1),
    reaction_time_hrs       NUMERIC(5,2),
    dmso_concentration_pct  NUMERIC(5,2),
    conjugation_yield_pct   NUMERIC(5,1)
);

CREATE TABLE IF NOT EXISTS manufacturing.purification (
    id                          SERIAL PRIMARY KEY,
    batch_number                VARCHAR(20) REFERENCES manufacturing.batches(batch_number),
    tff_passes                  INTEGER,
    purification_recovery_pct   NUMERIC(5,1),
    final_concentration_mg_ml   NUMERIC(6,2)
);

CREATE TABLE IF NOT EXISTS manufacturing.raw_materials (
    id                  SERIAL PRIMARY KEY,
    batch_number        VARCHAR(20) REFERENCES manufacturing.batches(batch_number),
    material            VARCHAR(50),
    lot_number          VARCHAR(20),
    quantity_used_g     NUMERIC(8,2)
);

-- ─── ANALYTICAL SCHEMA ───────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS analytical.analytical_results (
    id                  SERIAL PRIMARY KEY,
    batch_number        VARCHAR(20) REFERENCES manufacturing.batches(batch_number),
    dar                 NUMERIC(4,2),
    dar_pass            BOOLEAN,
    sec_purity_pct      NUMERIC(5,2),
    sec_pass            BOOLEAN,
    endotoxin_eu_ml     NUMERIC(6,3),
    endotoxin_pass      BOOLEAN,
    bioburden_sterility VARCHAR(10),
    bioburden_pass      BOOLEAN
);

-- ─── QUALITY SCHEMA ──────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS quality.deviations (
    deviation_id    VARCHAR(10) PRIMARY KEY,
    batch_number    VARCHAR(20) REFERENCES manufacturing.batches(batch_number),
    deviation_type  VARCHAR(100),
    severity        VARCHAR(20) CHECK (severity IN ('Minor', 'Major', 'Critical')),
    date_raised     DATE,
    status          VARCHAR(25)
);
