#!/bin/bash

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo "tmux is not installed. Please install it first:"
    echo "For macOS: brew install tmux"
    echo "For Ubuntu/Debian: sudo apt-get install tmux"
    exit 1
fi

# Create a new tmux session
tmux new-session -d -s finance_assistant

# Function to create a new window and run a service
create_window() {
    local window_name=$1
    local command=$2
    tmux new-window -t finance_assistant -n "$window_name" "$command"
}

# Start each service in a new window
create_window "orchestrator" "uvicorn backend.orchestrator.main:app --reload --port 8000"
create_window "api_agent" "uvicorn backend.agents.api_agent.main:app --reload --port 8001"
create_window "scraping_agent" "uvicorn backend.agents.scraping_agent.main:app --reload --port 8002"
create_window "retrieval_agent" "uvicorn backend.agents.retrieval_agent.main:app --reload --port 8003"
create_window "language_agent" "uvicorn backend.agents.language_agent.main:app --reload --port 8005"
create_window "streamlit" "streamlit run streamlit_app.py"

# Attach to the tmux session
echo "Starting all services in tmux session 'finance_assistant'..."
echo "Use 'tmux attach -t finance_assistant' to view the services"
echo "Use 'Ctrl+b d' to detach from the session"
echo "Use 'Ctrl+b n' to switch between windows"
echo "Use 'Ctrl+b &' to close a window"
echo "Use 'tmux kill-session -t finance_assistant' to stop all services"

# Attach to the session
tmux attach -t finance_assistant 