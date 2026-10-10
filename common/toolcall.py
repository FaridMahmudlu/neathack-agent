"""Minimal OpenAI-format tool calling: JSON schemas generated from Python
callables, plus a bounded dispatch loop shared by both agents."""

import inspect
import json


def _ptype(annotation) -> dict:
    s = getattr(annotation, "__name__", str(annotation))
    if "int" in s:
        return {"type": "integer"}
    if "float" in s:
        return {"type": "number"}
    if "bool" in s:
        return {"type": "boolean"}
    if "list" in s:
        return {"type": "array", "items": {"type": "string"}}
    if "dict" in s:
        return {"type": "object"}
    return {"type": "string"}


def _schema(fn) -> dict:
    sig = inspect.signature(fn)
    props, required = {}, []
    for name, p in sig.parameters.items():
        props[name] = _ptype(p.annotation)
        if p.default is inspect.Parameter.empty:
            required.append(name)
    return {
        "type": "function",
        "function": {
            "name": fn.__name__,
            "description": inspect.getdoc(fn) or "",
            "parameters": {
                "type": "object",
                "properties": props,
                "required": required,
            },
        },
    }


def run_agent(client, model: str, system: str, tool_fns: list, goal: str, max_steps: int = 30) -> str:
    registry = {fn.__name__: fn for fn in tool_fns}
    tools = [_schema(fn) for fn in tool_fns]
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": goal},
    ]
    for _ in range(max_steps):
        resp = client.chat.completions.create(
            model=model, messages=messages, tools=tools
        )
        msg = resp.choices[0].message
        messages.append(msg.model_dump(exclude_none=True))
        calls = msg.tool_calls or []
        if not calls:
            return msg.content or "(no answer)"
        for call in calls:
            fn = registry.get(call.function.name)
            try:
                args = json.loads(call.function.arguments or "{}")
                out = fn(**args) if fn else f"error: unknown tool {call.function.name}"
            except Exception as exc:
                out = f"error: {exc}"
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "name": call.function.name,
                    "content": str(out)[:20000],
                }
            )
    return "(step limit reached)"
