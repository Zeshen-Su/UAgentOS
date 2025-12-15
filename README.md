# UAgentOS
An Agent framework that autonomously orchestrates custom tools and AI reasoning to accomplish complex tasks.

## 🚀 Usage

1.  **Define Your Tools**: Create your custom scripts and place them in the toolsetdirectory. Each toolset should have a corresponding TOOL.mdfile describing its purpose and available functions. The framework automatically translates a toolset's meta-functions into actionable Tool classes for the AI agent. 
2.  **Define Your Prompt**: The agent prompt is in the `agent.yaml`.
3.  **Set Your Goal**: Modify the user_request variable in mini.pyto define your task objective. The agent will then autonomously plan and execute the necessary tool operations to achieve it.

Understanding the Toolset-Tool Hierarchy:
1.  A Toolset​ represents a functional domain (e.g., math), containing logically grouped operations
2.  Individual Tools​ perform specific actions within that domain (e.g., add, subtract)
3.  The agent intelligently selects and orchestrates Tools from appropriate Toolsets to fulfill complex tasks, maintaining clear logical layering

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
