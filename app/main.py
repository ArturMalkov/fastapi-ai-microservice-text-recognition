import pathlib

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


BASE_DIR = pathlib.Path(__file__).parent


app = FastAPI()
templates = Jinja2Templates(directory=rf"{BASE_DIR}\templates")


@app.get("/", response_class=HTMLResponse)  # this response class expects HTML string to be returned
def home_view(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "abc": 123})


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
