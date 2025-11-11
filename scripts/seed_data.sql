-- ===========================================
-- 📘 AgroSense Tech - Base de Datos PostgreSQL
-- Datos simulados de sensores IoT agrícolas
-- ===========================================


-- ======================
-- Tabla: sensor_data
-- ======================
-- Drop dependent view first if it exists (Postgres will prevent dropping table otherwise)
DROP VIEW IF EXISTS sensor_metrics;
DROP TABLE IF EXISTS sensor_data;

CREATE TABLE sensor_data (
    id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(20) NOT NULL,
    temperature DECIMAL(5,2) NOT NULL,
    humidity DECIMAL(5,2) NOT NULL,
    ph DECIMAL(4,2) NOT NULL,
    light DECIMAL(7,2) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ======================
-- Datos de ejemplo reales
-- ======================

INSERT INTO sensor_data (sensor_id, temperature, humidity, ph, light, timestamp) VALUES
('S-101', 24.5, 68.2, 6.7, 425.0, '2025-11-10 06:00:00'),
('S-101', 25.1, 70.0, 6.8, 440.5, '2025-11-10 07:00:00'),
('S-101', 26.0, 72.4, 6.9, 455.2, '2025-11-10 08:00:00'),
('S-101', 27.5, 73.5, 7.0, 480.8, '2025-11-10 09:00:00'),
('S-101', 29.1, 74.0, 7.1, 510.0, '2025-11-10 10:00:00'),

('S-102', 22.8, 66.4, 6.6, 410.3, '2025-11-10 06:00:00'),
('S-102', 23.4, 68.0, 6.6, 420.7, '2025-11-10 07:00:00'),
('S-102', 24.3, 69.8, 6.7, 432.2, '2025-11-10 08:00:00'),
('S-102', 25.0, 71.0, 6.8, 450.6, '2025-11-10 09:00:00'),
('S-102', 26.2, 72.3, 6.9, 465.1, '2025-11-10 10:00:00'),

('S-103', 20.4, 61.0, 6.5, 390.1, '2025-11-10 06:00:00'),
('S-103', 21.0, 63.5, 6.5, 400.4, '2025-11-10 07:00:00'),
('S-103', 22.1, 65.7, 6.6, 410.9, '2025-11-10 08:00:00'),
('S-103', 23.3, 68.0, 6.7, 430.5, '2025-11-10 09:00:00'),
('S-103', 24.5, 70.2, 6.8, 450.0, '2025-11-10 10:00:00');

-- ======================
-- Vista de métricas
-- ======================
CREATE OR REPLACE VIEW sensor_metrics AS
SELECT
    sensor_id,
    ROUND(AVG(temperature), 2) AS avg_temp,
    ROUND(AVG(humidity), 2) AS avg_humidity,
    ROUND(AVG(ph), 2) AS avg_ph,
    ROUND(AVG(light), 2) AS avg_light,
    MAX(temperature) AS max_temp,
    MIN(temperature) AS min_temp,
    MAX(humidity) AS max_humidity,
    MIN(humidity) AS min_humidity,
    MAX(light) AS max_light,
    MIN(light) AS min_light
FROM sensor_data
GROUP BY sensor_id;

-- ======================
-- Consulta de prueba
-- ======================
SELECT * FROM sensor_metrics;
