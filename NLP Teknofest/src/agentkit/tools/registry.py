# src/agentkit/tools/registry.py
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, create_model
from langchain.tools import StructuredTool

from agentkit.tools.schemas import function_schemas
from agentkit.tools import api_functions as api

function_map = {s["name"]: getattr(api, s["name"]) for s in function_schemas}

def _jsonschema_to_pytype(schema: Dict[str, Any]) -> Any:
    t = schema.get("type", "string")
    if t == "string":
        return str
    if t == "integer":
        return int
    if t == "number":
        return float
    if t == "boolean":
        return bool
    if t == "array":
        item_schema = schema.get("items", {"type": "string"})
        return List[_jsonschema_to_pytype(item_schema)]  # type: ignore
    if t == "object":
        return Dict[str, Any]
    return Any

def build_args_schemas(function_schemas: List[Dict[str, Any]]) -> Dict[str, type[BaseModel]]:
    out: Dict[str, type[BaseModel]] = {}
    for f in function_schemas:
        params = f.get("parameters", {}) or {}
        props: Dict[str, Any] = params.get("properties", {}) or {}
        required = set(params.get("required", []) or [])
        fields: Dict[str, tuple[Any, Any]] = {}
        for pname, pschema in props.items():
            ptype = _jsonschema_to_pytype(pschema)
            pdesc = pschema.get("description")
            if pname in required:
                fields[pname] = (ptype, Field(..., description=pdesc))
            else:
                fields[pname] = (Optional[ptype], Field(None, description=pdesc))  # type: ignore
        model_name = f"{f.get('name','Tool')}Args"
        out[f["name"]] = create_model(model_name, __base__=BaseModel, **fields)  # type: ignore
    return out

def build_structured_tools() -> List[StructuredTool]:
    args_schemas = build_args_schemas(function_schemas)
    tools: List[StructuredTool] = []
    for s in function_schemas:
        tools.append(
            StructuredTool.from_function(
                func=function_map[s["name"]],
                name=s["name"],
                description=s.get("description", ""),
                args_schema=args_schemas[s["name"]],
                infer_schema=False,
            )
        )
    return tools

tools = build_structured_tools()
