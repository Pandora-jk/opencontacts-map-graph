#!/bin/bash
# spawn-specialist.sh
# Spawns a specialized agent with department-specific context

DEPT=$1
TASK=$2

if [ -z "$DEPT" ] || [ -z "$TASK" ]; then
    echo "Usage: spawn-specialist.sh <department> <task>"
    echo "Departments: finance, coding, travel, infra"
    exit 1
fi

DEPT_PATH="/home/ubuntu/.openclaw/workspace/departments/$DEPT"

if [ ! -d "$DEPT_PATH" ]; then
    echo "Error: Department '$DEPT' not found."
    exit 1
fi

echo "🚀 Spawning $DEPT specialist for task: $TASK"

# Load department context files
CONTEXT_FILES="$DEPT_PATH/SOUL.md $DEPT_PATH/MEMORY.md $DEPT_PATH/TODO.md"

# Spawn the agent with isolated context
# Note: This uses the sessions_spawn tool pattern
# In practice, this would call the OpenClaw API with the specific context
sessions_spawn \
    --label "$DEPT-specialist" \
    --agent "$DEPT" \
    --mode run \
    --task "$TASK" \
    --context "$CONTEXT_FILES"

echo "✅ Specialist spawned. Check session logs for progress."
