import yaml
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates

from include import cpg
from include.cgl import logger

router = APIRouter(
    prefix="/gateway",
    tags=["Gateway"]
)

templates = Jinja2Templates(directory="templates")


@router.get("/")
def gw_index(request: Request):
    # gw_list = sorted(cpg.list_gateways(),
    #             key=lambda gw: gw.get('descr_file', {}).get('dmn'), reverse=True)
    gw_list = cpg.list_gateways()
    gw_list_ext = []
    for item in gw_list:
        temp_item = item.model_dump()
        # Additional fields for easier processing in the template
        temp_item.update({
            "mgmt_name": temp_item['descr_file']['annotation']['mgmt_name'],
            "dmn": temp_item['descr_file']['annotation']['dmn'],
        })
        gw_list_ext.append(temp_item)
    content = yaml.dump(
        [item.model_dump(by_alias=True) for item in gw_list],
        indent=4, Dumper=cpg.MyDumper)
    # logger.debug(content)
    return templates.TemplateResponse(router.prefix+"/index.html", {
        "title":"Index",
        "gw_list": gw_list_ext,
        "content": content,
        "request": request
    })


@router.get("/{mgmt_server}/{dmn}/{name}")
def gw_details(request:Request, mgmt_server, dmn, name):
    gw = cpg.gateway_by_name(mgmt_server, dmn, name)
    content = yaml.dump(gw.model_dump(), indent=4, Dumper=cpg.MyDumper)
    return templates.TemplateResponse(router.prefix+"/gw_details.html", {
        "title":"Asset details",
        "content": content,
        # "content": f"<p>Mgmt_server: {mgmt_server}</p><p>DMN {dmn}</p><p>Asset {asset}</p>",
        "request": request,
    })
