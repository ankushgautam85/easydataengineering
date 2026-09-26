# ATUF Reader Lab — release 1.0.2

Companion to *Engineering Modern Data Pipelines* by Ankush Gautam.

**Mac:** start Docker Desktop, stop any earlier ATUF containers, extract this ZIP into a new folder, then open **Start_Lab.command** in Finder. The launcher creates the Python environment and runs the suite without command pasting or file edits. Open **Stop_Lab.command** when finished.

Python 3.11+, Docker Desktop / Compose v2, Bash and curl 7.76.0+ are required. No pip packages are needed. The download is an unsigned script package; macOS may require its normal approval UI.

See [START_HERE.md](START_HERE.md) for prerequisites, Linux/WSL commands, expected results and troubleshooting. See [TESTING.md](TESTING.md) for verification evidence and limitations.

Final acceptance target: 40 unique orders, USD 1,180.00 and zero lag on Kafka partitions 0, 1 and 2. The full suite includes an intentional outage/recovery drill.

Updates: https://github.com/ankushgautam85/easydataengineering

The lab uses synthetic data and disables authentication. Keep it local. No GitHub upload was performed by this packaging task.
