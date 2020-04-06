#!/bin/bash

set -e
# --------------------------- PARAMETERS NEEDED -------------------------------
export FACTORIO_DIR_PATH=
export TELEGRAM_CHANNEL_ID=
export TELEGRAM_BOT_TOKEN=
export RCON_PWD=

# --------------------------- OPTIONAL PARAMETERS -------------------------------
# export FACTORIO_HOST=127.0.0.1

# Get script location
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Backup console.log
touch "$FACTORIO_DIR_PATH"/console-previous.log
touch "$FACTORIO_DIR_PATH"/console.log
cat "$FACTORIO_DIR_PATH"/console.log >> "$FACTORIO_DIR_PATH"/console-previous.log
rm "$FACTORIO_DIR_PATH"/console.log

/usr/bin/python3 "$DIR"/main.py &

"$FACTORIO_DIR_PATH"/bin/x64/factorio --server-settings "$FACTORIO_DIR_PATH"/data/server-settings.json --start-server-load-latest --port 25565 --rcon-port 27015 --rcon-password "$RCON_PWD" --console-log "$FACTORIO_DIR_PATH"/console.log
