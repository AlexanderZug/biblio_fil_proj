import arrow

from fastapi import FastAPI, Request, Form, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from starlette import status


app = FastAPI(max_body_size=1000000)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def read_bibliography(request: Request, bibliography: str = Query(None)):
    current_year = arrow.now().year
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "current_year": current_year,
            "bibliography": bibliography,
        }
    )


@app.post("/create_bibliography", response_class=HTMLResponse)
def create_bibliography(
    bibliography: str = Form(...),
):
    return RedirectResponse(
        url=f"/?bibliography={bibliography}",
        status_code=status.HTTP_302_FOUND,
    )
