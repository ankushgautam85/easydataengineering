# Release 1.0.2

- Removed unsupported Logstash command-line options. Validation now uses only `--config.test_and_exit` and `--path.data /tmp/logstash-validation`, both documented for Logstash 8.19.
- Retained persistent queue and DLQ settings in logstash.yml; validation uses separate temporary storage.
- Added `-T` to the remaining Kafka container command so captured runs do not require an interactive terminal.
- Retained Kafka volume ownership initialization, bounded HTTP startup/recovery retries and telemetry disconnect handling.
- Numbered shell steps change to their own directory before accessing local files.
- Added Start_Lab.command and Stop_Lab.command with automatic venv setup and a stable unique project name per extracted folder.
- Added early checks for occupied ports and existing fixtures/volumes; no automatic data deletion.
- Reports retain failed stages and timeout details and refuse to overwrite an earlier run. Diagnostics inspect only configured image references.
- Strengthened verification of order/event ID correspondence and exact Kafka partition identities.
- Added shell-command behavioral tests, a real HTTP disconnect test, and launcher/reporting regression tests.
