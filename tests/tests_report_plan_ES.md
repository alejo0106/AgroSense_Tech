| ID | Nombre de la Prueba | Tipo | Estado |
|----|----------------------|------|--------|
| CP-SENS-01 | test_sensor_data_post_valid | Prueba Unitaria | Completada |
| CP-SENS-02 | test_sensor_data_post_invalid | Prueba Unitaria | Completada |
| CP-PROC-01 | test_process_data_correctness | Prueba Unitaria | Completada |
| CP-PROC-02 | test_process_data_empty | Prueba Unitaria | Completada |
| CP-AN-01 | test_analytics_endpoint_consistency | Prueba de Integración | Completada |
| CP-DB-01 | test_dashboard_load | Prueba de Integración | Completada |
| CP-DB-02 | test_dashboard_empty_state | Prueba de Integración | Completada |
| CP-E2E-01 | test_end_to_end_ingest_and_metrics | Prueba de Sistema | Completada |
| CP-LEG-01 | test_placeholder_cleanup (analytics legacy) | Legado | Conservado |
| CP-LEG-02 | test_placeholder_cleanup_dashboard | Legado | Conservado |
| CP-LEG-03 | test_placeholder_cleanup_sensor | Legado | Conservado |
| CP-LEG-04 | test_placeholder_cleanup_sensors_dup | Legado | Conservado |
| CP-FIX-01 | client fixture available | Fixture de Pruebas | Completada |
| CP-FIX-02 | db_session fixture cleanup | Fixture de Pruebas | Completada |
| CP-COV-01 | Coverage >= 80% core modules | Calidad | Completada (91% total) |
| CP-COV-02 | Add coverage for database helpers | Calidad | Completada (database.py 88%) |
| CP-COV-03 | Add coverage for sensor_simulator script | Calidad | Pendiente |

Nota: Este plan de pruebas se desarrolló siguiendo las normas ISO/IEC 25010 e ISO/IEC 29119, garantizando cobertura funcional, trazabilidad y repetibilidad.
