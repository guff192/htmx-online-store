# Create tmux windows & set the names
tmux rename-window -t htmx-online-store:0 'local-server'
tmux new-window -n 'editor' -t htmx-online-store:

# Split the server window vertically
tmux split-window -v -t htmx-online-store:local-server.0

# Split the bottom pane in server window horizontally
tmux split-window -h -t htmx-online-store:local-server.1

# Change env variables with sed
sed -I .bak 's/\(TESTING=\).*/\1False/g' ./.env && rm ./.env.bak
sed -I .bak 's/\(DB_URL=".*\/\).*"/\1products"/g' ./.env && rm ./.env.bak

# Activate the virtual environment in top pane & clear it
tmux send-keys -t htmx-online-store:local-server.0 'source ./venv/bin/activate' Enter
tmux send-keys -t htmx-online-store:local-server.0 C-l

# Run the app in the top pane
tmux send-keys -t htmx-online-store:local-server.0 'python -B -m app' Enter

# Run public dev endpoint for the app
tmux send-keys -t htmx-online-store:local-server.1 'ngrok http 42069' Enter

# Run the postgres server & connect to it in the right bottom pane & clear it
tmux send-keys -t htmx-online-store:local-server.2 'pg_ctl -D /usr/local/var/postgresql@17 restart && psql -h localhost -p 5432 -d postgres' Enter
tmux send-keys -t htmx-online-store:local-server.2 C-l

# Create the 'products' database in the right bottom pane & connect to it & clear it
tmux send-keys -t htmx-online-store:local-server.2 'CREATE DATABASE products\;' Enter
tmux send-keys -t htmx-online-store:local-server.2 '\c products' Enter
tmux send-keys -t htmx-online-store:local-server.2 C-l

# Activate the virtual environment & open neovim in editor window
tmux send-keys -t htmx-online-store:editor 'source ./venv/bin/activate' Enter
tmux send-keys -t htmx-online-store:editor 'nvim' Enter
