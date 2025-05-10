#!/usr/bin/env bash

current_session=$(tmux display-message -p '#S')

# define current OS
if [[ "$(uname -s)" == *"Darwin"* ]]; then
    CURRENT_OS=MacOS
elif [[ "$(uname -s)" == *"Linux"* ]]; then
    CURRENT_OS=Linux
else
    CURRENT_OS="Something else"
fi


# Create tmux windows & set the names
tmux rename-window -t $current_session:0 'local-server'
tmux new-window -n 'editor' -t $current_session:

# Split the server window vertically
tmux split-window -v -t $current_session:local-server.0

# Split the bottom pane in server window horizontally
tmux split-window -h -t $current_session:local-server.1

# Change env variables with sed
if [[ $CURRENT_OS == "Linux" ]]; then
    sed -i 's/\(TESTING=\).*/\1False/g' ./.env
    sed -i 's/\(DB_URL=".*\/\).*"/\1products"/g' ./.env
elif [[ $CURRENT_OS == "MacOS" ]]; then
    sed -I .bak 's/\(TESTING=\).*/\1False/g' ./.env && rm ./.env.bak
    sed -I .bak 's/\(DB_URL=".*\/\).*"/\1products"/g' ./.env && rm ./.env.bak
fi

# Activate the virtual environment in top pane & clear it
tmux send-keys -t $current_session:local-server.0 'source ./venv/bin/activate' Enter
tmux send-keys -t $current_session:local-server.0 C-l

# Ensure tailwindcss and tailwindcss/cli are installed
tmux send-keys -t $current_session:local-server.0 'npm install' Enter

# Run the app in the top pane
tmux send-keys -t $current_session:local-server.0 'python -B -m app' Enter

# Run public dev endpoint for the app
tmux send-keys -t $current_session:local-server.1 'ngrok http 42069' Enter

# Run the postgres server & connect to it in the right bottom pane & clear it
if [[ $CURRENT_OS == "Linux" ]]; then
    tmux send-keys -t $current_session:local-server.2 'su postgres -c "/usr/local/pgsql/bin/pg_ctl -D /usr/local/pgsql/data restart" && \
        psql -h localhost -p 5432 -U postgres -c "CREATE DATABASE products;"; \
        psql -h localhost -p 5432 -U postgres -d products' Enter
elif [[ $CURRENT_OS == "MacOS" ]]; then
    tmux send-keys -t $current_session:local-server.2 'pg_ctl -D /usr/local/var/postgresql@17 restart && \
        psql -h localhost -p 5432 -U postgres -c "CREATE DATABASE products;"; \
        psql -h localhost -p 5432 -U postgres -d products' Enter
    tmux send-keys -t $current_session:local-server.2 C-l
fi

# Activate the virtual environment & open neovim in editor window
tmux send-keys -t $current_session:editor 'source ./venv/bin/activate' Enter
tmux send-keys -t $current_session:editor 'nvim' Enter
