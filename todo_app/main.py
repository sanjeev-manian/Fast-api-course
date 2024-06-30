from fastapi import FastAPI, Request
from fastapi import status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from . import routers

# models.Base.metadata.create_all(bind=engine)
# for first time creating database, with our class schema
app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def redirect_to_home_page(request: Request):
    return RedirectResponse("/home", status_code=status.HTTP_302_FOUND)


app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(routers.router)
