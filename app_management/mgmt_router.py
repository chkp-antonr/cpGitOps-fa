import yaml
from fastapi import APIRouter, Request #, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import asyncio

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

    if mgmt_server:
        # Managing Server is selected
        logger.debug(f"Prepare a list of domains (in SSoT) for {mgmt_server}")
        try:
            if mgmt_server:
                matched = next((server for server in list_domains
                                if server.descr_file.annotation.name == mgmt_server), None)
                if matched:
                    domains = [dmn[0] for dmn in cpf.show_domains(mgmt_server)]
                    domains.append("Global")
                    content = f"<p>Domains in SSoT: {matched.dmns}</p>" \
                            f"<p>Domains on MDM: {domains}</p>"
        except AssertionError as e:
            logger.error(f"diff/show_domains: {e}")

        commands = cpf.Mgmt().enum_mgmt_api_calls_for_ver()

        if action == "diff":
            if domain:
                diff_domains = [domain]
            else:
                diff_domains = domains
            if command:
                diff_commands = [command]
            else:
                diff_commands = commands

            logger.info(f"Find diff for {mgmt_server}/ {diff_domains} {diff_commands}")
            diff = await cpf.mgmt_diff(mgmt_server, diff_domains, diff_commands)
            logger.warning(f"\n{diff}")
            return templates.TemplateResponse(router.prefix+"/diff_show.html", {
                "title":"Diff show",
                "content": "",
                "diff": diff,
                "request": request})


        #     pass

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

# def details_asset(request, mgmt_server, dmn, asset):
#     # asset name or uuid
#     return render(request, "management/details_asset.html", {
#         "title":"Asset details",
#         "content": f"<p>Mgmt_server: {mgmt_server}</p><p>DMN {dmn}</p><p>Asset {asset}</p>",
#         })

@router.get("/get_status")
async def test_get_status(request: Request, action:str=""):
    # logger.debug(message[0])
    return { "message": message[0] }