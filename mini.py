#!/usr/bin/env python3

import json
import os
import yaml
import inspect
import re
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

from brain import get_brain_response
from src.models.litellm_model import LitellmModel
from src.tools.protocol import Tool, ToolSet
from src.tools.registry import registry
from src.memory.core import memory  

load_dotenv()

# Load agent.yaml
with open(os.path.join(os.path.dirname(__file__), "agent.yaml"), "r", encoding="utf-8") as f:
    AGENT_CONFIG = yaml.safe_load(f)
    MINI_CONFIG = AGENT_CONFIG.get("mini", {})


MINI_PROVIDER = os.getenv("MINI_PROVIDER", "default-provider")
MINI_MODEL_NAME = os.getenv("MINI_MODEL_NAME", "default-model")
MINI_API_KEY = os.getenv("MINI_API_KEY", "default-key")
MINI_API_URL = os.getenv("MINI_API_URL", "default-url")
MINI_CONFIGURED = os.getenv("MINI_CONFIGURED", "false").lower() == "true"

MINI_LLM: Optional[LitellmModel] = None


def _initialise_mini_model() -> Optional[LitellmModel]:
    if not MINI_CONFIGURED:
        print(" Mini 模型未配置，工具将无法使用 LLM 功能。")
        return None
    return LitellmModel(
        api_key=MINI_API_KEY,
        model_name=MINI_MODEL_NAME,
        api_base=MINI_API_URL,
        custom_llm_provider=MINI_PROVIDER,
    )


def _format_tool_definitions(tools: List[Tool]) -> str:
    return json.dumps([tool.get_definition() for tool in tools], indent=2, ensure_ascii=False)


def _select_tool_and_args(user_request: str, tools: List[Tool], llm: LitellmModel) -> Optional[Dict[str, Any]]:
    prompt = MINI_CONFIG["tool_selection_user_template"].format(
        user_request=user_request,
        tool_definitions=_format_tool_definitions(tools)
    )
    template = MINI_CONFIG["tool_selection_system_prompt"]
    response = llm.generate_response(task=prompt, template=template)

    try:
        json_str = response.strip()
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0].strip()
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0].strip()

        if json_str.lower() == "null":
            return None

        return json.loads(json_str)
    except (json.JSONDecodeError, IndexError):
        print(f"无法解析工具选择的 LLM 响应: {response}")
        return None


def _execute_tool(toolset: ToolSet, user_request: str, llm: LitellmModel) -> str:
    tools = toolset.get_tools()
    if not tools:
        return f"工具集 '{toolset.name}' 未提供任何工具。"

    selection = _select_tool_and_args(user_request, tools, llm)
    if not selection or "tool" not in selection:
        # 回退机制
        print(f"未找到匹配工具，尝试使用 LLM 直接回答: {user_request}")
        fallback_prompt = MINI_CONFIG["generic_request_template"].format(
            reason=f"No suitable tool found in toolset '{toolset.name}' for request: {user_request}"
        )
        # 将用户请求附加到回退提示中以提供上下文
        full_fallback_prompt = f"{fallback_prompt}\n\nUser Request: {user_request}"
        fallback_response = llm.generate_response(task=full_fallback_prompt, template="You are a helpful assistant.")
        return fallback_response

    tool_name = selection["tool"]
    arguments = selection.get("arguments", {})
    
    chosen_tool: Optional[Tool] = next((t for t in tools if t.name == tool_name), None)
    if not chosen_tool:
        return f"选择的工具 '{tool_name}' 在工具集 '{toolset.name}' 中不存在。"

    try:
        print(f"正在执行工具: {tool_name}，参数: {arguments}")
        tool_output = chosen_tool.execute(**arguments)
        print(f"工具输出: {tool_output}")

        # 稳健性要求：如果工具返回了原始数据，请用LLM对其进行格式化
        if "format" in user_request.lower() or "provide the answer" in user_request.lower():
            print("DEBUG: Detected formatting request. Using LLM to format tool output...")
            final_prompt = MINI_CONFIG["tool_execution_user_template"].format(
                user_request=user_request,
                tool_name=tool_name,
                tool_output=tool_output
            )
            formatted_response = llm.generate_response(
                task=final_prompt, 
                template="You are a helpful assistant. If the user asks for a specific format, follow it strictly."
            )
            return formatted_response

        # Return the raw tool output directly
        return str(tool_output)

    except Exception as e:
        return f"执行工具 '{tool_name}' 时出错: {e}"


def run_toolset(name: str, instruction: str) -> str:
    """
    Exposed API for the generated script to call a toolset.
    """
    # 稳健性修复：如果f-string失败，则自动插值变量
    # #如果指令包含{var_name}并且该var存在于调用者的作用域中，则替换它。
    try:
    #我们通过确保括号后面没有引号来避免匹配像{“key”：…}这样的JSON结构。
    #像{content}这样的简单变量将被匹配。
        if re.search(r'\{[a-zA-Z_]\w*\}', instruction):
            frame = inspect.currentframe()
            if frame and frame.f_back:
                caller_locals = frame.f_back.f_locals
                
                def replacer(match):
                    var_name = match.group(0)[1:-1] # remove braces
                    if var_name in caller_locals:
                        val = caller_locals[var_name]
                        return str(val)
                    return match.group(0)
                
                new_instruction = re.sub(r'\{([a-zA-Z_]\w*)\}', replacer, instruction)
                if new_instruction != instruction:
                    print(f"DEBUG: Detected un-interpolated variables. Auto-fixing instruction...")
                    instruction = new_instruction
    except Exception as e:
        print(f"DEBUG: Auto-interpolation failed: {e}")

    print(f"\n>>> 调用工具集: {name} | 指令: {instruction}")
    
    if MINI_LLM is None:
        return "Error: Mini LLM not initialized."

    toolset_instance = registry.create(name)
    if not toolset_instance:
        return f"Error: Toolset '{name}' not found."

    try:
        result = _execute_tool(toolset_instance, instruction, MINI_LLM)
        print(f"<<< 工具集返回: {result}\n")
        return result
    except KeyboardInterrupt:
        print("\n[用户中断了工具执行]")
        raise  


def main() -> None:
    global MINI_LLM
    MINI_LLM = _initialise_mini_model()
    if not MINI_LLM:
        return
    
    print("Agent 已启动。请输入你的需求 (输入 'exit' 退出)。")

    while True:
        try:
            user_input = input("\nUser: ").strip()
        except KeyboardInterrupt:
            print("\n(输入 'exit' 退出)")
            continue
        except EOFError:
            print("\nExiting...")
            break

        if not user_input:
            continue
        
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        memory.add_message("user", user_input)

        try:
            response = get_brain_response(user_input)
        except KeyboardInterrupt:
            print("\n[用户中断了思考]")
            continue  
        
        resp_type = response.get("type", "question")
        content = response.get("content", "")

        if resp_type == "question":
            print(f"\nAgent (Question): {content}")
            memory.add_message("assistant", content)
        
        elif resp_type == "plan":
            print(f"\nAgent (Plan): {content}")
            print("\n(请确认该计划，或者提出修改意见)")
            memory.add_message("assistant", content)
            
        elif resp_type == "code":
            print("\nAgent: 正在执行任务...")
            print(f"DEBUG: Generated Code:\n{'-'*20}\n{content}\n{'-'*20}")
            execution_context = {
                "run_toolset": run_toolset,
                "print": print,
                "range": range,
                "len": len,
                "str": str,
                "int": int,
                "list": list,
                "dict": dict,
                "Presentation": None, 
                "BytesIO": None     
            }
            
            try:
                from pptx import Presentation
                from io import BytesIO
                execution_context["Presentation"] = Presentation
                execution_context["BytesIO"] = BytesIO
            except ImportError:
                pass

            try:
                exec(content, execution_context)
                # 回退后要保留历史记录以便后续解答用户问题
                memory.add_message("assistant", "Task executed successfully.")
            except KeyboardInterrupt:
                print("\n[用户中断了任务执行]")
                memory.add_message("assistant", "Task interrupted by user.")
            except Exception as e:
                print(f"执行计划时出错: {e}")
                memory.add_message("assistant", f"Execution failed: {e}")
        
        else:
            print(f"Unknown response type: {resp_type}")

if __name__ == "__main__":
    main()
