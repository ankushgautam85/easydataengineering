# Verification evidence — release 1.0.2

## What passed in the build environment

23 unit/regression tests passed, covering exact counts, amounts, currencies, event/order identity correspondence, retained batch preservation, Kafka lag parsing, telemetry rejection and retry behavior, and these additional regressions:

- Executed step_09.sh with a simulated Docker command contract: supported Logstash flags, isolated validation path, service startup only after successful validation.
- Executed step_12.sh with simulated Docker: no terminal required by either Kafka command.
- Ran telemetry.py against a real local HTTP server that deliberately closed the first connection and accepted the retried request.
- Checked stable project identity, invalid saved-project rejection, preservation of prior fixtures, rejection of existing volumes, actionable port-conflict errors, and accurate failed-stage/timeout reporting.

Python compilation, Bash syntax, YAML parsing and ZIP integrity checks also passed. The release has no virtual environments, generated events, previous reports or Python caches in the archive.

## Documentation review

The two Logstash options used by step_09.sh are listed in the version-specific command-line documentation:
https://www.elastic.co/guide/en/logstash/8.19/running-logstash-command-line.html

Queue and dead-letter-queue settings remain in the settings file:
https://www.elastic.co/guide/en/logstash/8.19/logstash-settings-file.html

## What is not certified

Docker and a Docker daemon are unavailable in the build environment. Simulated command-contract tests are not real Logstash execution. This exact release has not completed the full Docker integration suite here. The Mac launchers have been syntax-checked; Finder execution and macOS download-security behavior have not been exercised on a Mac here. Do not describe this package as universally working or as a fully integration-tested release.

The author previously supplied a successful end-to-end run on macOS / Apple Silicon and Python 3.14.6 after manual repairs. A subsequent fresh run of the preceding ZIP exposed the unsupported Logstash CLI flags now removed. Those observations are useful regression evidence, not a complete unattended pass for this exact release.

## Release gate

A full unattended `test_all.py` PASS on a fresh Docker host is still required before publishing a verified-release claim. The suite records Python/host details, Docker/Compose versions, configured image digests, stage logs and final acceptance results. A unit-test pass cannot substitute for this gate.
