import json
import pathlib

import typer
from fastapi.openapi.utils import get_openapi

from app.operations_api_contract import app


def main(output: pathlib.Path = pathlib.Path("openapi.json")):
    with output.open("w") as f:
        json.dump(
            get_openapi(
                title=app.title,
                version=app.version,
                openapi_version=app.openapi_version,
                description=app.description,
                routes=app.routes,
            ),
            f,
        )


if __name__ == "__main__":
    typer.run(main)
