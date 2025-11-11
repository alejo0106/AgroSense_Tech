| ID | Nombre | Tipo | Estado |
|----|--------|------|--------|
| CP-SENS-01 | test_sensor_data_post_valid | Unit | Done |
| CP-SENS-02 | test_sensor_data_post_invalid | Unit | Done |
| CP-PROC-01 | test_process_data_correctness | Unit | Done |
| CP-PROC-02 | test_process_data_empty | Unit | Done |
| CP-AN-01 | test_analytics_endpoint_consistency | Integration | Done |
| CP-DB-01 | test_dashboard_load | Integration | Done |
| CP-DB-02 | test_dashboard_empty_state | Integration | Done |
| CP-E2E-01 | test_end_to_end_ingest_and_metrics | System | Done |
| CP-LEG-01 | test_placeholder_cleanup (analytics legacy) | Legacy | Retained |
| CP-LEG-02 | test_placeholder_cleanup_dashboard | Legacy | Retained |
| CP-LEG-03 | test_placeholder_cleanup_sensor | Legacy | Retained |
| CP-LEG-04 | test_placeholder_cleanup_sensors_dup | Legacy | Retained |
| CP-FIX-01 | client fixture available | Fixture | Done |
| CP-FIX-02 | db_session fixture cleanup | Fixture | Done |
| CP-COV-01 | Coverage >= 80% core modules | Quality | Done (91% total) |
| CP-COV-02 | Add coverage for database helpers | Quality | Done (database.py 88%) |
| CP-COV-03 | Add coverage for sensor_simulator script | Quality | Pending |

Nota: Los tests *legacy* se mantienen como placeholders documentando la consolidación (# cleanup) para trazabilidad sin duplicar lógica.