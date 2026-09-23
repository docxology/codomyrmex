#!/bin/bash
# Jules Batch Dispatcher
# Dispatches multiple concurrent coding tasks to Google Jules coding agent.

if [ "$#" -ne 1 ]; then
    echo "Usage: ./jules_batch_dispatch.sh <tasks_file.md>"
    echo "Each non-empty line in the tasks file will launch a new Jules parallel agent session."
    exit 1
fi

TASKS_FILE=$1
REPO="docxology/codomyrmex"

if [ ! -f "$TASKS_FILE" ]; then
    echo "Error: Tasks file $TASKS_FILE not found."
    exit 1
fi

echo "Dispatching Jules agents to repository: $REPO"
echo "------------------------------------------------"

# Read tasks ignoring empty lines and comments
job_count=0
while IFS= read -r task || [ -n "$task" ]; do
    # Skip empty lines and comments
    if [[ -z "$task" ]] || [[ "$task" == \#* ]]; then
        continue
    fi

    echo "Launching Agent for task: $task"
    # Launch in background to achieve concurrency
    jules new --repo "$REPO" "$task" > /dev/null 2>&1 &
    job_count=$((job_count + 1))

    # Optional slight delay to avoid hammering the initial API handshake
    sleep 1
done < "$TASKS_FILE"

echo "------------------------------------------------"
echo "Dispatched $job_count parallel Jules agents."
echo "Use 'jules remote list --session' to monitor progress."
echo "Use 'jules remote pull --session <ID> --apply' to merge completed work."
