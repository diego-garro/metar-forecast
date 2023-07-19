import asyncio

from fastapi import FastAPI, Path
from fastapi.responses import FileResponse
from typing_extensions import Annotated

from .forecast import make_forecast
from .tojson import to_json


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World!"}


@app.get("/{station}.json")
async def forecast(station: str = Path(..., regex=r"mr[a-z][a-z]")):
    file_path = f"./data/json/{station}.json"

    return FileResponse(file_path)


@app.get("/{station}.txt")
async def forecast(station: str = Path(..., regex=r"mr[a-z][a-z]")):
    file_path = f"./data/txt/{station}.txt"

    return FileResponse(file_path)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
