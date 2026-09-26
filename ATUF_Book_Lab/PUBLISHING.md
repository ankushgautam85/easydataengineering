# Publishing the reader codebase

Target repository: https://github.com/ankushgautam85/easydataengineering

1. Run the rebuilt package's complete acceptance suite in a fresh environment. Review every stage and retain the generated report and environment information.
2. Place this source folder under `book-lab/` in the repository. Keep the README, reader guide, tests and configurations with the executable examples.
3. Exclude `.venv/`, `__pycache__/`, generated batches, Docker data and test logs using the supplied `.gitignore`. Review the staged diff before committing. The manuscript and publisher assets are not part of this ZIP.
4. Select an appropriate code license consistent with the publishing agreement before describing the repository as open source. This task does not select or grant a license.
5. Commit and push the reviewed source, then tag the successfully tested commit, for example `book-v1.0.0`. Do not label an untested commit as integration-tested.
6. Build the reader ZIP from that same tagged source. Maintain one source of truth rather than divergent author and reader copies.
7. Keep the baseline tag available; publish later changes with their own release notes and test evidence. Check book listings when behavior changes.

Readers can use this same codebase once it is pushed to the public repository. Merely adding a repository URL to the book does not publish the code. No GitHub upload, commit or release was performed in this packaging task.
