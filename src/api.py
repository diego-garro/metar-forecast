import json

from fastapi import FastAPI, Path, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .station import Stations


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static/templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    stations = Stations()
    return templates.TemplateResponse(
        "index.html", {"request": request, "stations": stations}
    )


@app.get("/forecast/{station}", response_class=HTMLResponse)
async def html_response(
    request: Request, station: str = Path(..., regex=r"mr[a-z][a-z]")
):
    file_path = f"./data/json/{station}.json"
    f = open(file_path)
    json_obj = json.load(f)
    context = {"request": request}
    context.update(json_obj)

    return templates.TemplateResponse("forecast.html", context)


@app.get("/{station}.json")
async def json_response(station: str = Path(..., regex=r"mr[a-z][a-z]")):
    file_path = f"./data/json/{station}.json"

    return FileResponse(file_path)


@app.get("/{station}.txt")
async def txt_response(station: str = Path(..., regex=r"mr[a-z][a-z]")):
    file_path = f"./data/txt/{station}.txt"

    return FileResponse(file_path)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
