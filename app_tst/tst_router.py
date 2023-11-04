import yaml
from fastapi import APIRouter, Request #, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from random import randint
import asyncio

from include import cpg
from include import cpf
from include.cgl import logger

router = APIRouter(
    prefix="/test",
    tags=["Test"]
)

templates = Jinja2Templates(directory="templates")

message = ""

async def tst_action(action=""):
    global message

    for i in range(10,20):
        # message = "<p>Test <strong>" + str(randint(10, 99)) + "</strong> " + action + "</p>"
        message = "<p>Test <strong>" + str(i) + "</strong> " + action + "</p>"
        logger.debug(message)
        await asyncio.sleep(1)
    # if randint(1,3) == 2:

    message = ""
    return

@router.get("/")
async def tst_index(request: Request, action="", get_status=None):
    # if not hasattr(test_index, "iter_no"):
    #   tsst_index.iter_no = 0  # it doesn't exist yet, so initialize it
    # try:
    #     print(test_index.iter_no)
    # except NameError:
    #     test_index.iter_no = 0

    content = "Test"
    # # for tests
    # from src import schemas as sch
    # from include import cpf
    # res = cpf.Mgmt().fetch_packages_dmn("mdmPrime", dmn="cpGitOps")
    # status, client = cpf.Mgmt().login(sch.ManagementToLogin(name="mdmPrime", dmn="cpGitOps"))
    # content=status

    # action without get_status - run actions and redirect to &get_status
    #
    logger.error(f"'{action}' - '{get_status}'")
    if action and (get_status is None):
        # tst_index.iter_no += 1
        # run something
        logger.info('Calling test_action')
        asyncio.create_task(test_action())
        logger.info('Redirecting')
        return RedirectResponse("?get_status")

    return templates.TemplateResponse(router.prefix+"/index.html", {
        "title":"Index",
        "content": content,
        "request": request})

@router.get("/get_status")
async def tst_get_status(request: Request, action:str=""):

    # status_updates = []
    # for i in range(5):
    #     status_updates.append(f"Processing... Step {i+1}")

    # return {"status": status_updates}

    # message = "<p>Test <strong>" + str(randint(10, 99)) + "</strong> " + action + "</p>"
    # if randint(1,3) == 2:
    #     message = ""
    # # for tests
    # from src import schemas as sch
    # from include import cpf
    # res = cpf.Mgmt().fetch_packages_dmn("mdmPrime", dmn="cpGitOps")
    # status, client = cpf.Mgmt().login(sch.ManagementToLogin(name="mdmPrime", dmn="cpGitOps"))
    # content=status
    logger.info(message)
    return { "message": message }
