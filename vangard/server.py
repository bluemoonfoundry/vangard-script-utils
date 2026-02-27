# server.py
import argparse
from typing import Any, Dict, List, Optional
import uvicorn
from fastapi import FastAPI, Body, HTTPException
from pydantic import create_model, BaseModel

from core.framework import load_config, build_parser, load_class, TYPE_MAP

def create_fastapi_app():
    """
    Dynamically creates the FastAPI app with endpoints from the configuration file.
    """
    config = load_config()
    app_config = config.get("app", {})
    
    app = FastAPI(
        title=app_config.get("prog", "GenericCLI Server"),
        description=app_config.get("description"),
    )

    @app.get("/", summary="Health Check", tags=["System"])
    def read_root():
        return {"status": "ok", "app": app_config.get("prog", "cli")}

    # --- CRITICAL CHANGE ---
    # The ArgumentParser is built ONCE here for efficiency. It can then be
    # passed to any command that needs it (like the 'help' command).
    parser = build_parser(config)

    for cmd_config in config.get("commands", []):
        command_name = cmd_config["name"]
        
        # --- Dynamically create a Pydantic model for the request body ---
        pydantic_fields = {}
        for arg in cmd_config.get("arguments", []):
            field_name = arg["dest"]
            field_type: Any = TYPE_MAP.get(arg.get("type", "str"), str)
            
            if arg.get("nargs") in ("*", "+"):
                field_type = List[field_type]
            
            if arg.get("action") == "store_true":
                field_type = bool
                pydantic_fields[field_name] = (Optional[field_type], False)
                continue

            default_value = arg.get("default")
            if arg.get("required", False):
                 pydantic_fields[field_name] = (field_type, ...)
            else:
                 pydantic_fields[field_name] = (Optional[field_type], default_value)

        # Create the dynamic Pydantic model for this command's arguments
        RequestModel = create_model(
            f"{command_name.replace('-', '_').capitalize()}Request", 
            **pydantic_fields,
            __base__=BaseModel
        )
        
        # --- Dynamically create the endpoint function ---
        # We use a factory function (closure) to correctly capture the
        # command's config and the shared parser instance for each iteration.
        def create_endpoint_func(cmd_cfg, model):
            async def endpoint(payload: model = Body(...)):
                try:
                    # Convert the Pydantic model to an argparse.Namespace
                    # so our existing command classes can use it without changes.
                    namespace = argparse.Namespace(**payload.dict(exclude_unset=True))
                    
                    CommandClass = load_class(cmd_cfg["class"])

                    # --- CRITICAL CHANGE ---
                    # Instantiate the command and pass the parser to its constructor.
                    command_instance = CommandClass(parser=parser, config=config)

                    result = command_instance.process(namespace)
                    
                    return {"result": result}
                except Exception as e:
                    # Raise a standard HTTP exception for any errors during command execution.
                    raise HTTPException(status_code=500, detail=str(e))
            return endpoint

        endpoint_func = create_endpoint_func(cmd_config, RequestModel)
        
        # Add the dynamically created endpoint to the FastAPI app
        app.post(
            f"/api/{command_name}",
            summary=cmd_config["help"],
            response_model=Dict[str, Any],
            tags=["Commands"]
        )(endpoint_func)

    return app

# The FastAPI app instance is created by calling our factory
app = create_fastapi_app()

def main():
    """
    The main entry point to run the FastAPI server using Uvicorn.
    """
    uvicorn.run("vangard.server:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()