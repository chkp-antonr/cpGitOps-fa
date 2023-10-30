
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
#
# from fastapi.responses import PlainTextResponse
# from starlette.exceptions import HTTPException as StarletteHTTPException
# from starlette.background import BackgroundTask
# import asyncio
#
from include.cpg import router as router_cpg # to see in docs
from include.cpf import router as router_cpf # to see in docs
from app_gateway.gw_router import router as router_gateway
from app_management.mgmt_router import router as router_management
from app_ticket.tkt_router import router as router_ticket
from include.cgl import logger, settings, prepare_logger
# https://github1s.com/artemonsh/fastapi_course/blob/main/Lesson_12/src/main.py#L3

# class Formatter(logging.Formatter):
#     def format(self, record):
#         if record.levelno == logging.DEBUG:
#             self._style._fmt = cgl.LOGFORMAT_DEBUG
#         else:
#             self._style._fmt = cgl.LOGFORMAT
#         return super().format(record)

@asynccontextmanager
# pylint: disable=redefined-outer-name,unused-argument
async def lifespan(app: FastAPI):
    prepare_logger()
    # logger.debug("Starting custom debug")
    # logger.info("Starting custom info")
    # logger.warning("Starting custom warning")
    # logger.critical("Starting custom critical")
    logger.info(f"Staring with SSoT={settings.DIR_SSOT}")
    yield
    # Clean up models and release the resources
    logger.warning("Good bye")

app = FastAPI(
    title="cpGitOps",
    lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router_cpf)
app.include_router(router_cpg)
app.include_router(router_gateway)
app.include_router(router_management)
app.include_router(router_ticket)

origins = [
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers",
                   "Access-Control-Allow-Origin", "Authorization"],
)

templates = Jinja2Templates(directory="templates")

# async def exit_app():
#     loop = asyncio.get_running_loop()
#     loop.stop()

# @app.exception_handler(StarletteHTTPException)
# async def http_exception_handler(request, exc):
#     task = BackgroundTask(exit_app)
#     return PlainTextResponse(str(exc.detail), status_code=exc.status_code, background=task)


@app.get("/")
def index(request: Request):
    content = "Main page"
    # # for tests
    # from src import schemas as sch
    # from include import cpf
    # status, client = cpf.MgmtL().login(sch.ManagementToLogin(name="mdmPrime", dmn="cpGitOps"))
    # content=status
    # logger.debug(status)

    return templates.TemplateResponse("index.html", {
        "title":"Main page",
        "content": content,
        "request": request})
