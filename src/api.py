import asyncio

from fastapi import FastAPI, Path, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static/templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


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
