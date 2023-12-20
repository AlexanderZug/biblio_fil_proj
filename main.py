import arrow
from fastapi import FastAPI, Request, Form, Query, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette import status

from bibliography_conversion import ArticleConverter

app = FastAPI(max_body_size=1000000)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


def get_current_year():
    return arrow.now().year


@app.get("/", response_class=HTMLResponse)
async def read_bibliography(request: Request, bibliography: str = Query(None)):
    current_year = get_current_year()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "current_year": current_year,
            "bibliography": bibliography,
        }
    )


@app.post("/create_bibliography", response_class=HTMLResponse)
async def create_bibliography(
    bibliography: str = Form(...),
):
    if not bibliography:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bibliography cannot be empty",
        )
    result = ArticleConverter(bibliography).get_bibliography()

    return RedirectResponse(
        url=f"/?bibliography={result}",
        status_code=status.HTTP_302_FOUND,
    )
