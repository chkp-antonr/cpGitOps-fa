import json
import yaml
from fastapi import APIRouter, Request, BackgroundTasks, WebSocket, WebSocketException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import asyncio

from typing import Text, List, Dict

from include import cpg
from include import cpf
from include.cgl import logger, settings

router = APIRouter(
    prefix="/management",
    tags=["Management"]
)

templates = Jinja2Templates(directory="templates")
message = [""]

@router.get("/")
def mgmt_index(request: Request):
    mgmt_list = cpg.list_mgmt_domains()
    content = yaml.dump(
        [item.model_dump(by_alias=True) for item in mgmt_list],
        indent=4, Dumper=cpg.MyDumper)
    return templates.TemplateResponse(router.prefix+"/index.html", {
        "title":"Index",
        "mgmt_list": mgmt_list,
        "content": content,
        "request": request})


@router.get("/dashboard/")
def mgmt_dashboard(request: Request):
    return templates.TemplateResponse(router.prefix+"/dashboard.html", {
        "title":"Dashboard",
        "request": request})

@router.get("/show_domains/")
@router.get("/show_domains/{mgmt_server}",
            description="Mgmt server name to filter by, actions:[update_ssot,fetch_api]")
async def mgmt_show_domains(request: Request, mgmt_server=None, action="", domain=""):
    # logger.debug(request.url.path)
    list_domains = cpg.list_mgmt_domains()
    mgmt_servers = [server.descr_file.annotation.name for server in list_domains
                    if server.descr_file.annotation.kind == "MDM"]
    content = "Select Management server to refresh its domains"
    update_ssot_result = None
    domains = []
    try:
        if mgmt_server:
            matched = next((server for server in list_domains
                            if server.descr_file.annotation.name == mgmt_server), None)
            if matched:
                domains = [dmn[0] for dmn in cpf.show_domains(mgmt_server)]
                content = f"<p>Domains in SSoT: {matched.dmns}</p>" \
                        f"<p>Domains on MDM: {domains}</p>"
    except AssertionError as e:
        logger.error(f"show_domains: {e}")

    update_ssot_result = {}
    if action == "update_ssot_dirs":
        logger.info("Update SSoT")
        update_ssot_result = cpf.update_ssot_mgmt_domains(mgmt_server)
    elif action == "fetch_api":
        logger.info(f"Fetch from API {mgmt_server}/{domain}")
        # fetch_last_result = cpf.fetch_api_mgmt_domains(mgmt_server, message)
        asyncio.create_task(cpf.fetch_api_mgmt_domains(mgmt_server, domain, message))
        logger.error('Redirecting')
        content = "Fetching from API"
        return RedirectResponse("?get_status")

    return templates.TemplateResponse(router.prefix+"/show_domains.html", {
        "title": "Show domains",
        "mgmt_servers": mgmt_servers,
        "mgmt_server": mgmt_server,
        "update_ssot_result": update_ssot_result,
        "content": content,
        "domains": domains,
        "request": request,
    })


# @router.get("/diff/",
#             description="Listbox with available file-names (commands show-*) and policy packages")
# async def mgmt_diff(request: Request, mgmt_server="", domain="", command="", action=""):
#     content = ""
#     commands = []
#     packages = []
#     mgmt_servers = []
#     domains = []

#     # Provide a list of available management servers
#     logger.debug("Prepare a list of management servers (in SSoT)")
#     list_domains = cpg.list_mgmt_domains()
#     mgmt_servers = [server.descr_file.annotation.name for server in list_domains
#             if server.descr_file.annotation.kind == "MDM"]

#     if mgmt_server:
#         # Managing Server is selected
#         logger.debug(f"Prepare a list of domains (in SSoT) for {mgmt_server}")
#         try:
#             if mgmt_server:
#                 matched = next((server for server in list_domains
#                                 if server.descr_file.annotation.name == mgmt_server), None)
#                 if matched:
#                     domains = [dmn[0] for dmn in cpf.show_domains(mgmt_server)]
#                     domains.append("Global")
#                     content = f"<p>Domains in SSoT: {matched.dmns}</p>" \
#                             f"<p>Domains on MDM: {domains}</p>"
#         except AssertionError as e:
#             logger.error(f"diff/show_domains: {e}")

#         commands = cpf.Mgmt().enum_mgmt_api_calls_for_ver()

#         if action == "diff":
#             if domain:
#                 diff_domains = [domain]
#             else:
#                 diff_domains = domains
#             if command:
#                 diff_commands = [command]
#             else:
#                 diff_commands = commands

#             logger.info(f"Find diff for {mgmt_server}/ {diff_domains} {diff_commands}")
#             diff = await cpf.mgmt_diff(mgmt_server, diff_domains, diff_commands, message)
#             logger.warning(f"\n{diff}")
#             message = [""]
#             return templates.TemplateResponse(router.prefix+"/diff_show.html", {
#                 "title":"Diff show",
#                 "content": "",
#                 "diff": diff,
#                 "request": request})
#         elif action == "sync_to_lastsaved":
#             if domain:
#                 diff_domains = [domain]
#             else:
#                 diff_domains = domains
#             if command:
#                 diff_commands = [command]
#             else:
#                 diff_commands = commands


#     return templates.TemplateResponse(router.prefix+"/diff.html", {
#         "title":"Diff",
#         "content": content,
#         "mgmt_servers": mgmt_servers,
#         "mgmt_server": mgmt_server,
#         "domains": domains,
#         "domain": domain,
#         "commands": commands,
#         "packages": packages,
#         "request": request})


@router.get("/diff/",
            description="Listbox with available file-names (commands show-*) and policy packages")
async def mgmt_diff(request: Request, mgmt_server="", domain="", command="", action=""):
    content = ""
    commands = []
    packages = []
    mgmt_servers = []
    domains = []

    # Provide a list of available management servers
    logger.debug("Prepare a list of management servers (in SSoT)")
    list_domains = cpg.list_mgmt_domains()
    mgmt_servers = [server.descr_file.annotation.name for server in list_domains
            if server.descr_file.annotation.kind == "MDM"]

#         elif action == "sync_to_lastsaved":
#             if domain:
#                 diff_domains = [domain]
#             else:
#                 diff_domains = domains
#             if command:
#                 diff_commands = [command]
#             else:
#                 diff_commands = commands

    return templates.TemplateResponse(router.prefix+"/diff.html", {
        "title":"Diff",
        "content": content,
        "mgmt_servers": mgmt_servers,
        "mgmt_server": mgmt_server,
        "domains": domains,
        "domain": domain,
        "commands": commands,
        "packages": packages,
        "request": request})


async def prepare_list_domains_commands(mgmt_server:Text) -> Dict:
    logger.debug(f"Prepare a list of domains (in SSoT) for {mgmt_server}")
    domains = []
    commands = []
    list_domains = cpg.list_mgmt_domains()
    try:
        if mgmt_server:
            matched = next((server for server in list_domains
                            if server.descr_file.annotation.name == mgmt_server), None)
            if matched:
                domains = [dmn[0] for dmn in cpf.show_domains(mgmt_server)]
                domains.append("Global")
                # content = f"<p>Domains in SSoT: {matched.dmns}</p>" \
                #         f"<p>Domains on MDM: {domains}</p>"
    except AssertionError as e:
        logger.error(f"diff/show_domains: {e}")

    commands = cpf.Mgmt().enum_mgmt_api_calls_for_ver()

    result = {
        "domains": domains,
        "commands": commands,
    }
    return result # prepare_list_domains_commands


async def mgmt_diff(websocket: WebSocket, mgmt_server:Text, domain:Text, command:Text):

    if not (domain and command):
        domain_command_list = await prepare_list_domains_commands(mgmt_server)

    if domain:
        diff_domains = [domain]
    else:
        diff_domains = domain_command_list['domains']
    if command:
        diff_commands = [command]
    else:
        diff_commands = domain_command_list['commands']


    logger.info(f"Find diff for {mgmt_server}/ {diff_domains} {diff_commands}")
    diff = await cpf.mgmt_diff(mgmt_server, diff_domains, diff_commands, websocket)
    logger.warning(f"\n{diff}")

    return diff # mgmt_diff

websockets = []

@router.websocket("/ws")
async def websocket(websocket: WebSocket):
    print("websocket")
    await websocket.accept()
    websockets.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                logger.debug(f"WebSocket message received: {data}")
                data = json.loads(data)
                result = {}
                if data.get('action') == "get_domains_list":
                    # logger.debug("get_domains_list")
                    result = await prepare_list_domains_commands(data.get('mgmt_server'))
                    result.update({"action": "domains_list"})
                elif data.get('action') == "diff":
                    logger.info(data)
                    diff = await mgmt_diff(websocket, data['mgmt_server'], data['domain'], data['command'])

                if result:
                    logger.debug(f"sending ws: {result}")
                    await websocket.send_json(result)

            except AttributeError as e:
                logger.error(f"WebSocket message: {data} error: {e}")

            await asyncio.sleep(1)  # Check for updates after every 5 seconds
    except WebSocketException:
        websockets.remove(websocket)
    return # websocket


@router.get("/get_status")
async def test_get_status(request: Request, action:str=""):
    # logger.debug(message[0])
    return { "message": message[0] }