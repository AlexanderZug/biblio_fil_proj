import arrow
from fastapi import FastAPI, Request, Form, Query, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette import status

from bibliography_conversion import ArticleConverter, BookConverter


app = FastAPI(max_body_size=1000000)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


def get_current_year() -> int:
    return arrow.now().year


@app.exception_handler(404)
async def not_found(request, exc)  -> HTMLResponse:
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)


@app.exception_handler(500)
async def internal_server_error(request, exc) -> HTMLResponse:
    return templates.TemplateResponse("500.html", {"request": request}, status_code=500)


@app.get("/", response_class=HTMLResponse)
async def read_bibliography(
    request: Request, bibliography: str = Query(None), source_type: str = Query(None)
) -> HTMLResponse:
    current_year = get_current_year()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "current_year": current_year,
            "source_type": source_type,
            "article_bibliography": bibliography if source_type == "article" else "",
            "book_bibliography": bibliography if source_type == "book" else "",
        },
    )


@app.post("/create_article", response_class=HTMLResponse)
async def create_article_bibliography(
    bibliography: str = Form(...),
) -> HTMLResponse:
    result = ArticleConverter(bibliography).get_bibliography()

    return RedirectResponse(
        url=f"/?bibliography={result}&source_type=article",
        status_code=status.HTTP_302_FOUND,
    )


@app.post("/create_book", response_class=HTMLResponse)
async def create_book_bibliography(
    bibliography: str = Form(...),
) -> HTMLResponse:
    result = BookConverter(bibliography).get_bibliography()

    return RedirectResponse(
        url=f"/?bibliography={result}&source_type=book",
        status_code=status.HTTP_302_FOUND,
    )
