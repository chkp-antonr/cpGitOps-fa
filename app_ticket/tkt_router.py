import json
import yaml
import asyncio
from fastapi import APIRouter, Request, Form, WebSocket, WebSocketException, WebSocketDisconnect, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from typing import Annotated, Dict, List

# from jinja2 import Template
from include import cpf
from include import cpg
from src import schemas as sch
from include.cgl import logger, settings

# from operations.router import get_specific_operations

router = APIRouter(
    prefix="/ticket",
    tags=["Ticket"]
)

templates = Jinja2Templates(directory="templates")

@router.get("/")
def index(request: Request):
    return templates.TemplateResponse(router.prefix+"/index.html", {"request": request})

@router.get("/add_host")
async def tkt_add_host(request: Request):
    list_domains = cpg.list_mgmt_domains()
    mgmt_servers = [server.descr_file.annotation.name for server in list_domains
                    if server.descr_file.annotation.kind == "MDM"]

    return templates.TemplateResponse(router.prefix+"/add_host.html", {
        "title": "Add host", "mgmt_servers": mgmt_servers, "request": request})


@router.post("/add_host")
async def add_host_post(request: Request,
                        mgmt_server:str = Form(""), domains:List[str] = Form([]), name:str = Form(""),
                        ipv4_address:str = Form(""), color:str = Form(), btn:str = Form(None) ):

    try:
        logger.warning(domains)

        added_host = sch.Upd_AddHost(
            mgmt=[sch.Upd_MGMT(name=mgmt_server, dmn=domains)],
            objects=[sch.Upd_Host(name=name, ipv4_address=ipv4_address, color=color)]
        )

        host_yaml = yaml.dump(added_host.model_dump(), indent=2, Dumper=cpg.MyDumper)
        logger.debug(f"\n{host_yaml}")

        try:
            fn = settings.DIR_UPD + "/hosts.yaml"
            with open(fn, "w") as yaml_file:
                yaml_file.write(host_yaml)
        except Exception as e:
            logger.error(f"Error writing {fn}: {e}")

        await cpg.ws_send_msg(websockets[0], f"Added host {name} {ipv4_address} {domains}")
        await asyncio.sleep(0.5)
    except HTTPException as e:
        logger.error(f"Form error: {e.detail}")
        # Handle error
        return {"error": str(e.detail)}

    return RedirectResponse("/ticket", status_code=status.HTTP_303_SEE_OTHER)

websockets:List[WebSocket]=[]


@router.websocket("/ws")
async def websocket(websocket: WebSocket):
    await websocket.accept()
    websockets.append(websocket)
    logger.debug(f"Websockets: {len(websockets)}")
    # await cpg.ws_send_msg(websocket, f"Websockets: {len(websockets)}")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                logger.debug(f"WebSocket message received: {data}")
                data = json.loads(data)
                result = {}
                if data.get('action') == "get_domains_list":
                    # logger.debug("get_domains_list")
                    result = await cpf.prepare_list_domains_commands(data.get('mgmt_server'))
                    result.update({"action": "domains_list"})
                # elif data.get('action') == "diff":
                #     # logger.info(data)
                #     diff = await mgmt_ws_diff(websocket, data['mgmt_server'], data['domain'], data['command'])
                # elif data.get('action') == "sync_to_saved":
                #     logger.info(data)
                #     await sync_to_saved(websocket, data['mgmt_server'], data['domain'], data['command'])

                if result:
                    # logger.debug(f"sending ws: {result}")
                    await websocket.send_json(result)

            except AttributeError as e:
                logger.error(f"WebSocket message: {data} error: {e}")

            await asyncio.sleep(1)  # Check for updates after every 5 seconds
    except (WebSocketException, WebSocketDisconnect) as e:
        # logger.debug(f"Websocket error: {e}")
        websockets.remove(websocket)
    return  # websocket
