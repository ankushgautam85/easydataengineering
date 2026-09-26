# ATUF Software Systems — reader lab guide

Release 1.0.2. Start with the Mac instructions below; no source edits are required.

## Mac: start without typing commands

1. Install Python 3.11+ and Docker Desktop if needed. Start Docker Desktop.
2. In Docker Desktop’s Containers view, stop earlier ATUF lab projects so ports 9200, 8080 and 4318 are free. Keep their volumes if you want to retain data.
3. Extract this ZIP into a new folder outside Trash. Keep the entire folder together.
4. In Finder, open `Start_Lab.command`. It changes to its own folder, creates `.venv`, assigns a unique project, and runs the complete test suite. If macOS displays a download-security prompt, follow its normal Open/approval UI; the launcher is an unsigned script, not a notarized app.
5. Wait for the report. Success requires every stage to pass and final status PASS.
6. Open `Stop_Lab.command` to stop this package’s project and preserve its data.

The launcher never deletes old lab data or stops unrelated containers. It records its project name in `.lab-project`. It preserves an existing report instead of overwriting it. For another full run, stop the current lab and extract a fresh copy. Detailed terminal instructions follow for Linux/WSL users and readers who prefer them.


Companion to *Engineering Modern Data Pipelines* by Ankush Gautam.

Code updates: https://github.com/ankushgautam85/easydataengineering

This guide covers a fresh installation, the full acceptance run, individual exercises, troubleshooting, and cleanup. Run commands in the extracted `ATUF_Book_Lab` folder. The Python code uses only the standard library. The four backend services run in Docker, not inside Python's virtual environment.

## 1. What you will build

The lab uses synthetic order events to demonstrate direct Elasticsearch ingestion, Logstash validation and quarantine, Kafka ingestion and duplicate handling, telemetry redaction, permission-filtered retrieval and deletion, and recovery after an outage. ATUF Software Systems is the fictional organization used in these examples.

| Component | Role | Bundled image tag / requirement |
|---|---|---|
| Python | Generate events and run checks | 3.11 or later; virtual environment |
| Elasticsearch | Store and query orders and retrieval documents | 8.19.0 |
| Kafka | Retain events and support recovery | 3.9.0 |
| Logstash | Validate, route and index events | 8.19.0 |
| OpenTelemetry Collector Contrib | Process and export synthetic logs | 0.120.0 |
| Kibana | Optional exploration UI | 8.19.0 |
| Docker | Run service containers | Engine with Compose v2 |
| Bash and curl | Execute numbered steps and HTTP requests | curl 7.76.0 or later |

Image tags are the edition baseline, not recommendations for production deployments. The earlier author run reported Collector version 0.120.1 even though the configured image tag was 0.120.0; the rebuilt package retains the configured tag. Record actual image digests and runtime versions when qualifying a release. Do not silently upgrade individual services and assume compatibility.

This is a local teaching lab with authentication disabled and host ports restricted to loopback. Do not expose the services publicly or use real personal or production data.

## 2. Install prerequisites once

- Python: https://www.python.org/downloads/
- Docker Desktop for macOS or Windows: https://docs.docker.com/desktop/
- Docker Engine / Compose for Linux: https://docs.docker.com/compose/install/

Start Docker Desktop and wait until its engine is running. Plan for roughly 8–12 GB available Docker memory and several GB of free disk for images and volumes. Startup time depends on the machine and network.

On macOS or Linux, use a Bash-compatible terminal. On Windows, use Ubuntu under WSL with Docker Desktop's WSL integration enabled; create the virtual environment inside WSL. These commands are not PowerShell commands. If Ubuntu cannot create a venv, install the distribution's `python3-venv` package and retry.

Check these commands before starting:

```bash
python3 --version
docker version
docker compose version
curl --version
```

Docker must show a reachable server. Compose must support v2. Host ports 9200, 8080 and 4318 must be free. Optional Kibana uses 5601. You do not need separate Java, Kafka, Logstash, Elasticsearch or Collector installations.

## 3. Extract and create the Python environment

Extract the ZIP into a new directory. Do not merge it into an old lab folder containing generated event files.

```bash
cd ATUF_Book_Lab
python3 -m venv .venv
source .venv/bin/activate
python -c "import sys; print(sys.executable); assert sys.prefix != sys.base_prefix"
```

No `pip install` command is required. Do not run `pip install .`: `setup.py` initializes Elasticsearch and is not a Python package installer.

Choose a Docker project name and use it consistently in this terminal:

```bash
export COMPOSE_PROJECT_NAME=atuf-book-lab
```

If the project already contains data, the full test runner refuses to overwrite it. Either use the explicit reset procedure below, or use a new project name in a fresh extracted folder. A new name creates separate Docker volumes; it does not avoid host-port conflicts. Stop the previous project first from its original folder.

## 4. Recommended: run the complete acceptance suite

This includes the outage drill, which stops only this lab's Elasticsearch and Logstash containers before restarting them.

```bash
python -m unittest discover -s tests -v
python test_all.py
```

The first command runs 23 unit/regression tests without Docker. The second command checks prerequisites, downloads the pinned images, runs every exercise and saves results. Do not run the individual stages first if you intend to use `test_all.py`; the full suite requires fresh local fixtures and fresh project volumes.

A successful suite ends with `"status": "PASS"` in `test-results/report.json`. Every listed stage must also show `PASS`. The final state is **40 unique orders totaling USD 1,180.00**, with all three Kafka partition lags at zero.

| Stage | What success establishes |
|---|---|
| unit | Fixture checks and telemetry retry/error behavior |
| install | Prerequisite checks, Compose configuration and image downloads |
| direct | 20 unique orders, USD 590.00, direct-v1; repeated ingestion keeps the same IDs |
| pipeline | 20 unique orders, USD 590.00, lab-v1; quarantine and Kafka delivery checks |
| kafka-lag | All three partitions consumed through their end offsets |
| telemetry / redaction | Synthetic log accepted and exported without its email attribute |
| retrieval | Permission-filter and deletion assertions complete |
| recovery | Retained second batch processed after services restart; 40 orders |
| recovery-lag / final-verify | Zero lag and final identities, amounts, currency and processing route |

Review `test-results/report.json`, stage logs, `services.log`, Docker/Compose version logs and image logs. The image digest inventory is restricted to the project’s configured images. The suite leaves services running for inspection.

The suite stops at the first failed stage, preserves the report, and refuses to overwrite a prior run. It never converts an earlier failed report into a pass just because you later run individual stages successfully. Preserve both the failed report and subsequent evidence. A clean full run is the release gate.

## 5. Alternative: learn one stage at a time

Use this sequence instead of the full runner on a fresh lab:

```bash
bash run_lab.sh install
bash run_lab.sh direct
bash run_lab.sh pipeline
python check_runtime.py lag
bash run_lab.sh telemetry
python check_runtime.py redaction
bash run_lab.sh retrieval
bash run_lab.sh verify 20
```

The telemetry command may print `200 {'partialSuccess': {}}`; an empty partial-success object contains no rejected-log count. Always run the redaction check as well. HTTP acceptance alone does not establish that sensitive attributes were removed.

The retrieval example uses synthetic three-dimensional vectors, not an external embedding model. It should end with `Deletion verified by document ID and employees query`.

Then run the outage drill once:

```bash
bash run_lab.sh recovery
python check_runtime.py lag
bash run_lab.sh verify 40
```

During the outage, Kafka has no active consumer and its lag increases. That is expected. After restart, the second batch must reach Elasticsearch and lag must drain to zero. Temporary connection errors during startup are retried; persistent errors still fail the stage.

Do not rerun `direct` after `pipeline`: it changes batch-a's processing route back to `direct-v1`. Do not rerun the normal pipeline checks after recovery; they expect 20 orders, while recovery intentionally leaves 40. Use `verify 40` for the recovered state.

## 6. Stop and resume without deleting data

```bash
bash run_lab.sh stop
deactivate
```

To resume in the same folder and with the same project name:

```bash
source .venv/bin/activate
export COMPOSE_PROJECT_NAME=atuf-book-lab
docker compose start elasticsearch kafka logstash otel
bash run_lab.sh verify 40
python check_runtime.py lag
```

Use `verify 20` if recovery has not run. Services can take time to become ready after a restart. Preserve `events.ndjson` and `batch-b.ndjson`: stable event identities make retries reproducible.

If recovery is interrupted, restart Elasticsearch and Logstash, then try `verify 40` and the lag check. If verification still fails, inspect the logs before republishing the retained batch. Do not regenerate or delete batch-b blindly. `step_14.sh` is an optional partition replay illustration, not a complete replay acceptance test.

## 7. Troubleshooting

Always activate the venv and export the same project name used for the run.

```bash
docker compose ps -a
docker compose logs --no-color --tail=150 elasticsearch kafka logstash otel
```

For a failed full-suite stage, inspect its log, for example:

```bash
tail -n 100 test-results/pipeline.log
```

| Symptom | What to check |
|---|---|
| Cannot connect to Docker daemon | Start Docker Desktop; verify WSL integration if applicable |
| Port already allocated | Stop the old lab from its original folder or identify the other application using the port |
| Existing volumes / fixtures refused | Use a fresh project and extraction, or deliberately reset the old synthetic lab |
| Kafka AccessDeniedException | Check `docker compose logs kafka-init`; the initializer must finish successfully before Kafka starts |
| Logstash queue lock during validation | Use this package's step_09.sh, which validates with a separate temporary data directory; do not delete live lock files |
| curl empty reply during startup | Bounded retries now handle this; if exhausted, inspect service logs and memory settings |
| Telemetry RemoteDisconnected | The sender now retries disconnects, connection failures and timeouts; persistent failures require Collector logs |
| HTTP 4xx / rejected telemetry records | Check payload and Collector configuration; the sender deliberately fails instead of concealing rejection |
| Final count or amount mismatch | Check which stages ran; preserve fixtures and inspect Elasticsearch/Logstash logs |
| Nonzero Kafka lag | Wait for recovery; inspect consumer and broker logs if the bounded check fails |
| Container exited / possible memory issue | Inspect `docker compose ps -a`, service logs and Docker resource settings |

For additional diagnostics, save the terminal output and the full `test-results/` folder. Do not report a successful fresh install until the full runner passes without manual intervention.

## 8. Deliberate reset of disposable lab data

This is optional and destructive: it removes only the selected Compose project's synthetic service data. First save logs and fixtures you want to retain. Confirm `COMPOSE_PROJECT_NAME` identifies the intended lab.

```bash
printf '%s\n' "$COMPOSE_PROJECT_NAME"
docker compose down --volumes --remove-orphans
```

Then extract the ZIP into another fresh folder and recreate the venv. A fresh extraction avoids deleting selected files manually. Reuse the project name only after its old volumes are removed. Never run `docker system prune` for this lab.

For a non-destructive fresh test, stop the old project, use a new extracted folder, and choose an unused name such as `atuf-book-lab-check`. Retain that name for all subsequent commands.

## 9. Optional Kibana

After Elasticsearch is ready:

```bash
docker compose up -d kibana
```

Open http://localhost:5601 after startup. Kibana is not required by the acceptance suite. Stop it with the rest of the project.

## 10. Files and updates

- `run_lab.sh`: individual lab stages and preflight.
- `test_all.py`: complete fresh-install acceptance sequence and reports.
- `tests/`: unit tests for assertions and telemetry failure handling.
- `compose.yaml`: pinned containers and Kafka volume initialization.
- `Start_Lab.command` / `Stop_Lab.command`: Mac launchers.
- `launch_lab.py`: automatic virtual-environment and project setup.
- `step_*.sh`: numbered book exercises with reliability fixes.
- `events.py`, `direct.py`, `setup.py`, `telemetry.py`, `retrieval.py`: example Python programs.
- `verify.py`, `check_runtime.py`: acceptance assertions.
- `orders.conf`, `logstash.yml`, `collector.yaml`: pipeline and telemetry configuration.
- `TESTING.md`: evidence and remaining verification limits.
- `CHANGELOG.md`: changes from the earlier bundle.
- `PUBLISHING.md`: maintainer instructions for publishing the same codebase.

Use https://github.com/ankushgautam85/easydataengineering for companion updates. Keep the edition release available and read release notes before updating. This package has not been uploaded to GitHub by this task.

Reference documentation:

- Python virtual environments: https://docs.python.org/3/library/venv.html
- Python HTTP disconnect exceptions: https://docs.python.org/3/library/http.client.html
- Logstash command-line overrides: https://www.elastic.co/guide/en/logstash/8.19/running-logstash-command-line.html
- Docker Compose: https://docs.docker.com/compose/
