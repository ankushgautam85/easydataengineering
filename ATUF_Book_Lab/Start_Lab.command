#!/bin/bash
cd -- "$(dirname -- "$0")" || exit 1
export PATH="/usr/local/bin:/opt/homebrew/bin:/Applications/Docker.app/Contents/Resources/bin:$PATH"
if command -v python3 >/dev/null 2>&1; then
  python3 launch_lab.py
  result=$?
else
  echo 'Python 3.11+ is required. Install it from https://www.python.org/downloads/.'
  result=1
fi
echo
if [ "$result" -eq 0 ]; then
  echo 'Finished. Review the result above. Close this window when ready.'
else
  echo 'The run did not pass. The output and any test-results logs explain the failure.'
fi
read -r -p 'Press Enter to close this window. ' _
exit "$result"
