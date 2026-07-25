Copilot Token-Efficiency Kit

A plugin-free implementation for GitHub Copilot Chat and Agent mode using:

-   RTK to compress terminal output.
-   Caveman Lite rules to reduce unnecessary response prose.
-   Ponytail-style rules to reduce unnecessary code, files, dependencies, and abstractions.
-   Existing CI, security scanning, and human review as quality gates.

This package assumes:

-   RTK is already installed and approved.
-   Copilot Chat and Agent mode are already enabled.
-   Your team already has global/user Copilot hooks containing telemetry logic.
-   Repository-level hooks must not replace or suppress global telemetry hooks.

Architecture decision

RTK is integrated into the existing user/global hook chain under ~/.copilot/hooks.

No .github/hooks directory is deployed to application repositories.

The recommended global PreToolUse order is:

1.  Existing telemetry/audit hook.
2.  Existing policy/security hook, when applicable.
3.  RTK command-rewrite hook as the final input-mutating hook.

Repository files contain only instructions, agents, skills, prompts, validation, and optional CI policy.

Deliverables

  File or directory                  Purpose
  ---------------------------------- --------------------------------------------------------------------------
  IMPLEMENTATION_PLAN.md             Enterprise execution and one-day rollout plan
  FILE_PLACEMENT_CHECKLIST.md        Exact global, endpoint, rollout, metrics, and .github placement sequence
  DEVELOPER_INSTALLATION_GUIDE.md    Separate instructions for every machine type
  GLOBAL_HOOK_INTEGRATION_GUIDE.md   Safely add RTK to existing telemetry hooks
  EFFICIENCY_MEASUREMENT_GUIDE.md    RTK, Copilot OTel, code, quality, and cycle-time metrics
  repository-template/.github        Files copied into each of the 14 repositories
  global-hooks                       Merge, verify, smoke-test, and rollback utilities
  developer-install                  Windows, macOS, Linux VDI, and Windows VDI scripts
  rollout                            Multi-repository deployment and rollback automation
  metrics                            RTK and Copilot OTel extraction and efficiency calculation
  tests                              Unit tests for the critical utilities

Fast implementation order

1.  Read GLOBAL_HOOK_INTEGRATION_GUIDE.md.
2.  Back up the current global telemetry hook file.
3.  Run global-hooks/merge_rtk_into_existing_hooks.py against that file.
4.  Apply global-hooks/vscode-settings.fragment.jsonc as a managed or user setting.
5.  Run global-hooks/verify_global_hooks.py.
6.  Pilot the repository template in two repositories.
7.  Fill rollout/repositories.csv.
8.  Run rollout/deploy_to_repositories.py --dry-run.
9.  Deploy to the 14 repositories.
10. Validate all four machine types.
11. Begin metrics collection using metrics/README.md.

Placement summary

Global/user machine locations

    ~/.copilot/hooks/
    └── <your-existing-telemetry-hook-file>.json

RTK is appended to the existing file. The package does not require a second hook file unless that is your preferred operational model.

Application repository locations

    <repo>/
    └── .github/
        ├── copilot-instructions.md
        ├── TOKEN-EFFICIENCY-VERSION
        ├── agents/
        ├── skills/
        ├── prompts/
        ├── instructions/
        └── scripts/

There is intentionally no .github/hooks directory.

Minimum commands

Merge RTK into an existing global hook file

    python3 global-hooks/merge_rtk_into_existing_hooks.py \
      --target "$HOME/.copilot/hooks/company-telemetry.json" \
      --command "/approved/path/rtk hook copilot"

Windows:

    py -3 global-hooks\merge_rtk_into_existing_hooks.py `
      --target "$HOME\.copilot\hooks\company-telemetry.json" `
      --command '"C:\Program Files\Company\RTK\rtk.exe" hook copilot'

Verify

    python3 global-hooks/verify_global_hooks.py \
      --hooks-dir "$HOME/.copilot/hooks" \
      --rtk-binary "/approved/path/rtk" \
      --telemetry-pattern "telemetry"

Deploy repository assets

    python3 rollout/deploy_to_repositories.py \
      --repositories rollout/repositories.csv \
      --template repository-template/.github \
      --workdir ./rollout-work \
      --dry-run

Remove --dry-run, then optionally use --push --create-pr after reviewing the generated changes.

Safety defaults

-   Existing hook files are backed up before modification.
-   RTK is added idempotently and never duplicated.
-   RTK errors fail open so the original command can run.
-   Repository hooks are rejected by validation.
-   Prompt or source content is not collected by the metrics scripts.
-   Copilot OpenTelemetry content capture remains disabled.
-   The rollout script merges a marked block into existing copilot-instructions.md instead of replacing it.
