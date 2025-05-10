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
tmux new-window -n 'tests' -t $current_session:

# Change env variables with sed
if [[ $CURRENT_OS == "Linux" ]]; then
    sed -i 's/\(TESTING=\).*/\1True/g' ./.env
    sed -i 's/\(DB_URL=".*\/\).*"/\1test_products"/g' ./.env
elif [[ $CURRENT_OS == "MacOS" ]]; then
    sed -I .bak 's/\(TESTING=\).*/\1True/g' ./.env && rm ./.env.bak
    sed -I .bak 's/\(DB_URL=".*\/\).*"/\1test_products"/g' ./.env && rm ./.env.bak
fi

# Split the server window vertically
tmux split-window -v -t $current_session:local-server.0

# Run the postgres server & connect to it in the right bottom pane & clear it
if [[ $CURRENT_OS == "Linux" ]]; then
    tmux send-keys -t $current_session:local-server.1 'su postgres -c "/usr/local/pgsql/bin/pg_ctl -D /usr/local/pgsql/data restart" && \
        psql -h localhost -p 5432 -U postgres -c "CREATE DATABASE test_products;"; \
        psql -h localhost -p 5432 -U postgres -d test_products' Enter

elif [[ $CURRENT_OS == "MacOS" ]]; then
    tmux send-keys -t $current_session:local-server.1 'pg_ctl -D /usr/local/var/postgresql@17 restart && \
        psql -h localhost -p 5432 -U postgres -c "CREATE DATABASE test_products;"; \
        psql -h localhost -p 5432 -U postgres -d test_products' Enter
    tmux send-keys -t $current_session:local-server.1 C-l
fi

# Activate the virtual environment & open neovim in editor window
tmux send-keys -t $current_session:editor 'source ./venv/bin/activate' Enter
tmux send-keys -t $current_session:editor 'nvim' Enter

# Activate the virtual environment & input the command to run the tests
tmux send-keys -t $current_session:tests.0 'source ./venv/bin/activate' Enter
tmux send-keys -t $current_session:tests.0 'pytest tests/'
