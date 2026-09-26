#!/bin/bash
cd -- "$(dirname -- "$0")" || exit 1
export PATH="/usr/local/bin:/opt/homebrew/bin:/Applications/Docker.app/Contents/Resources/bin:$PATH"
python3 launch_lab.py stop
result=$?
echo 'Stopping preserves the lab data.'
read -r -p 'Press Enter to close this window. ' _
exit "$result"
