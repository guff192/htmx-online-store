current_session=$(tmux display-message -p '#S')

# Create tmux windows & set the names
tmux rename-window -t $current_session:0 'local-server'
tmux new-window -n 'editor' -t $current_session:
tmux new-window -n 'tests' -t $current_session:

# Change env variables with sed
sed -I .bak 's/\(TESTING=\).*/\1True/g' ./.env && rm ./.env.bak
sed -I .bak 's/\(DB_URL=".*\/\).*"/\1test_products"/g' ./.env && rm ./.env.bak

# Split the server window vertically
tmux split-window -v -t $current_session:local-server.0

# Run the postgres server & connect to it in the right bottom pane & clear it
tmux send-keys -t $current_session:local-server.1 'pg_ctl -D /usr/local/var/postgresql@17 restart && psql -h localhost -p 5432 -d postgres' Enter
tmux send-keys -t $current_session:local-server.1 C-l

# Create the 'products' database in the right bottom pane & connect to it & clear it
tmux send-keys -t $current_session:local-server.1 'CREATE DATABASE test_products\;' Enter
tmux send-keys -t $current_session:local-server.1 '\c test_products' Enter
tmux send-keys -t $current_session:local-server.1 C-l


# Activate the virtual environment & open neovim in editor window
tmux send-keys -t $current_session:editor 'source ./venv/bin/activate' Enter
tmux send-keys -t $current_session:editor 'nvim' Enter

# Activate the virtual environment & input the command to run the tests
tmux send-keys -t $current_session:tests.0 'source ./venv/bin/activate' Enter
tmux send-keys -t $current_session:tests.0 'pytest tests/'
