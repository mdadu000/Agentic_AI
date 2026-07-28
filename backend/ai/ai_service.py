import json
import inspect
import asyncio
import uuid
from typing import Dict, List, Any, Optional, AsyncGenerator

from ai.groq_client import get_groq_client
from ai.prompts import SYSTEM_PROMPT
from agent import tools as agent_tools

# In-memory session store
_sessions: Dict[str, Dict[str, Any]] = {}

def _json_serialize(obj: Any) -> Any:
    """Converts Pydantic objects, datetimes, and custom types to JSON serializable objects."""
    def default_encoder(o):
        if hasattr(o, "model_dump"):
            return o.model_dump(mode="json")
        if hasattr(o, "dict"):
            return o.dict()
        if hasattr(o, "__dict__"):
            return o.__dict__
        if hasattr(o, "isoformat"):
            return o.isoformat()
        return str(o)

    return json.loads(json.dumps(obj, default=default_encoder))

class AIService:
    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        self.model_name = model_name
        self.tool_functions: Dict[str, Any] = {}
        self.tools_schema: List[Dict[str, Any]] = []
        self._register_tools()

    def _register_tools(self):
        """Registers all Python tools from agent.tools as function tools."""
        tool_names = [
            "get_all_restaurants",
            "add_restaurant",
            "get_menu_items_for_restaurant",
            "add_menu_item",
            "add_reservation",
            "add_user_review",
            "filter_restaurants_by_cuisine_tool",
            "search_for_menu_items_tool",
            "update_menu_item_price_tool",
            "remove_restaurant_tool",
            "remove_menu_item_tool",
            "get_reservations_today_tool",
            "get_highest_average_rating_restaurant",
            "get_best_rated_category_dish",
            "get_reservations_per_cuisine_type_tool",
            "get_most_recent_restaurant",
            "list_large_reservations",
            "get_restaurant_with_most_menu_items",
            "get_all_reservations_tool"
        ]

        for name in tool_names:
            func = getattr(agent_tools, name, None)
            if func and callable(func):
                self.tool_functions[name] = func
                schema = self._build_function_schema(func, name)
                self.tools_schema.append(schema)

    def _build_function_schema(self, func: Any, name: str) -> Dict[str, Any]:
        """Converts function signature to OpenAI/Groq function schema."""
        sig = inspect.signature(func)
        doc = (func.__doc__ or "").strip()

        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            if param_name in ('self', 'cls'):
                continue
            
            annotation = param.annotation
            schema_type = "string"
            if annotation in (int,):
                schema_type = "integer"
            elif annotation in (float,):
                schema_type = "number"
            elif annotation in (bool,):
                schema_type = "boolean"

            properties[param_name] = {
                "type": schema_type,
                "description": f"Parameter {param_name}"
            }

            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        return {
            "type": "function",
            "function": {
                "name": name,
                "description": doc,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }

    # Session CRUD Operations
    def create_session(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        sid = session_id or str(uuid.uuid4())
        _sessions[sid] = {
            "id": sid,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT}
            ],
            "events": []
        }
        return {"id": sid}

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return _sessions.get(session_id)

    def list_sessions(self) -> List[Dict[str, Any]]:
        return [{"id": sid} for sid in _sessions.keys()]

    def delete_session(self, session_id: str) -> bool:
        if session_id in _sessions:
            del _sessions[session_id]
            return True
        return False

    async def run_sse(self, session_id: str, user_message: str) -> AsyncGenerator[str, None]:
        """
        Direct Groq API streaming execution using groq_client.chat.completions.create.
        Yields Server-Sent Event formatted chunks matching frontend requirements.
        """
        groq_client = get_groq_client()
        session = self.get_session(session_id)
        if not session:
            session = self.create_session(session_id)

        # Append User Message
        session["messages"].append({"role": "user", "content": user_message})
        session["events"].append({
            "content": {
                "role": "user",
                "parts": [{"text": user_message}]
            }
        })

        max_turns = 5
        turn_count = 0

        while turn_count < max_turns:
            turn_count += 1
            
            try:
                # Direct Groq API call with fallback model support
                try:
                    response = await groq_client.chat.completions.create(
                        model=self.model_name,
                        messages=session["messages"],
                        tools=self.tools_schema if self.tools_schema else None,
                        tool_choice="auto" if self.tools_schema else None,
                        temperature=0.3,
                        stream=True
                    )
                except Exception as primary_err:
                    # Fallback to llama-3.1-8b-instant if primary model times out or encounters network load
                    fallback_model = "llama-3.1-8b-instant"
                    response = await groq_client.chat.completions.create(
                        model=fallback_model,
                        messages=session["messages"],
                        tools=self.tools_schema if self.tools_schema else None,
                        tool_choice="auto" if self.tools_schema else None,
                        temperature=0.3,
                        stream=True
                    )
            except Exception as err:
                error_payload = {
                    "sessionId": session_id,
                    "content": {
                        "role": "model",
                        "parts": [{"text": f"**Error:** Groq API call failed: {str(err)}"}]
                    }
                }
                yield f"data: {json.dumps(error_payload)}\n\n"
                break

            accumulated_text = ""
            tool_calls_accumulator = {}

            async for chunk in response:
                delta = chunk.choices[0].delta if chunk.choices else None
                if not delta:
                    continue

                if delta.content:
                    accumulated_text += delta.content
                    sse_payload = {
                        "sessionId": session_id,
                        "content": {
                            "role": "model",
                            "parts": [{"text": delta.content}]
                        }
                    }
                    yield f"data: {json.dumps(sse_payload)}\n\n"

                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        idx = tc.index
                        if idx not in tool_calls_accumulator:
                            tool_calls_accumulator[idx] = {
                                "id": tc.id or f"call_{idx}",
                                "name": tc.function.name if tc.function and tc.function.name else "",
                                "args_str": tc.function.arguments if tc.function and tc.function.arguments else ""
                            }
                        else:
                            if tc.function and tc.function.name:
                                tool_calls_accumulator[idx]["name"] += tc.function.name
                            if tc.function and tc.function.arguments:
                                tool_calls_accumulator[idx]["args_str"] += tc.function.arguments

            if accumulated_text:
                session["messages"].append({"role": "assistant", "content": accumulated_text})
                session["events"].append({
                    "content": {
                        "role": "model",
                        "parts": [{"text": accumulated_text}]
                    }
                })

            if tool_calls_accumulator:
                tool_calls_list = list(tool_calls_accumulator.values())
                
                assistant_tool_msg = {
                    "role": "assistant",
                    "content": accumulated_text or None,
                    "tool_calls": [
                        {
                            "id": tc["id"],
                            "type": "function",
                            "function": {
                                "name": tc["name"],
                                "arguments": tc["args_str"]
                            }
                        }
                        for tc in tool_calls_list
                    ]
                }
                session["messages"].append(assistant_tool_msg)

                for tc in tool_calls_list:
                    tool_name = tc["name"]
                    args_str = tc["args_str"]
                    call_id = tc["id"]

                    try:
                        args = json.loads(args_str) if args_str else {}
                        if not isinstance(args, dict):
                            args = {}
                    except Exception:
                        args = {}

                    # Notify frontend of tool invocation
                    fn_call_payload = {
                        "sessionId": session_id,
                        "content": {
                            "role": "model",
                            "parts": [{"functionCall": {"name": tool_name, "args": args}}]
                        }
                    }
                    yield f"data: {json.dumps(fn_call_payload)}\n\n"
                    session["events"].append(fn_call_payload)

                    # Execute function
                    tool_func = self.tool_functions.get(tool_name)
                    if tool_func:
                        try:
                            if asyncio.iscoroutinefunction(tool_func):
                                raw_result = await tool_func(**args)
                            else:
                                raw_result = tool_func(**args)
                        except Exception as ex:
                            raw_result = {"error": f"Tool execution failed: {str(ex)}"}
                    else:
                        raw_result = {"error": f"Tool '{tool_name}' not found."}

                    result_serialized = _json_serialize(raw_result)

                    # Notify frontend of tool response
                    fn_resp_payload = {
                        "sessionId": session_id,
                        "content": {
                            "role": "model",
                            "parts": [{"functionResponse": {"name": tool_name, "response": result_serialized}}]
                        }
                    }
                    yield f"data: {json.dumps(fn_resp_payload)}\n\n"
                    session["events"].append(fn_resp_payload)

                    session["messages"].append({
                        "role": "tool",
                        "tool_call_id": call_id,
                        "content": json.dumps(result_serialized)
                    })

                continue
            else:
                break

        yield "data: [DONE]\n\n"

# Export singleton AI Service
ai_service_instance = AIService()
