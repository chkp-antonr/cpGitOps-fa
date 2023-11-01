import yaml
from fastapi import APIRouter, Request #, Form, Depends
from fastapi.templating import Jinja2Templates

from include import cpg
from include import cpf
from include.cgl import logger

router = APIRouter(
    prefix="/management",
    tags=["Management"]
)

templates = Jinja2Templates(directory="templates")


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

@router.get("/show_domains/",
            description="{mgmt_server} Mgmt server name to filter by, actions:[update_ssot,fetch_api]")
def mgmt_show_domains(request: Request, mgmt_server=None, action=""):
    # logger.debug(request.url.path)
    list_domains = cpg.list_mgmt_domains()
    mgmt_servers = [server.descr_file.annotation.name for server in list_domains
                    if server.descr_file.annotation.kind == "MDM"]
    content = "Select Management server to refresh its domains"
    if mgmt_server:
        matched = next((server for server in list_domains
                        if server.descr_file.annotation.name == mgmt_server), None)
        if matched:
            domains = [dmn[0] for dmn in cpf.show_domains(mgmt_server)]
            content = f"<p>Domains in SSoT: {matched.dmns}</p>" \
                      f"<p>Domains on MDM: {domains}</p>"

    update_ssot_result = {}
    if action == "update_ssot_dirs":
        logger.info("Update SSoT")
        update_ssot_result = cpf.update_ssot_mgmt_domains(mgmt_server)
    elif action == "fetch_api":
        logger.warning("Fetch from API")
        fetch_last_result = cpf.fetch_api_mgmt_domains(mgmt_server)


    return templates.TemplateResponse(router.prefix+"/show_domains.html", {
        "title": "Show domains",
        "mgmt_servers": mgmt_servers,
        "mgmt_server": mgmt_server,
        "update_ssot_result": update_ssot_result,
        "content": content,
        "request": request,
    })


# def details_dmn(request, mgmt_server, dmn):
#     return render(request, "management/details_dmn.html", {
#         "title":"DMN details",
#         "content": f"<p>Mgmt_server: {mgmt_server}</p><p>DMN {dmn}</p>",
#         })


# def details_asset(request, mgmt_server, dmn, asset):
#     # asset name or uuid
#     return render(request, "management/details_asset.html", {
#         "title":"Asset details",
#         "content": f"<p>Mgmt_server: {mgmt_server}</p><p>DMN {dmn}</p><p>Asset {asset}</p>",
#         })
