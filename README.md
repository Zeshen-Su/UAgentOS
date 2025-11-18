# UAgentOS
A minimalism Agent framework. Users can define custom scripts, and the Agent autonomously call them to fulfill tasks.

## 🚀 Usage

1.  **Define Your Tools**: Place your custom scripts in the `python_tools`.
2.  **Declare Tools**: Inform the agent about the available tools by declaring them in the `agent.yaml`.
3.  **Set Your Goal**: Modify the `user_request` variable in `mini.py` to define your task objective. The agent will then autonomously work to complete it.

## ⚙️ LLM Configuration

The agent requires access to LLM APIs. Both the `Brain` (for planning) and the `mini-agent` (for execution) need to be configured separately.

You must create `.env` file in the project's root directory with the following exact variable names, providing your own API details:

MINI_PROVIDER=' '
MINI_MODEL_NAME=' '
MINI_API_KEY=' '
MINI_API_URL=' '
MINI_CONFIGURED='true'

BRAIN_PROVIDER=' '
BRAIN_MODEL_NAME=' '
BRAIN_API_KEY=' '
BRAIN_API_URL=' '
BRAIN_CONFIGURED='true'

**Important**: Ensure the variable names match exactly. Never commit your `.env` file to version control.
