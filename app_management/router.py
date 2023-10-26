import yaml
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates

from include import cpg
from include.cgl import logger

router = APIRouter(
    prefix="/management",
    tags=["Management"]
)

templates = Jinja2Templates(directory="templates")


@router.get("/")
def index(request: Request):
    mgmt_list = cpg.list_mgmt_domains()
    content = yaml.dump(mgmt_list, indent=4, Dumper=cpg.MyDumper)
    return templates.TemplateResponse(router.prefix+"/index.html", {
        "title":"Index",
        "mgmt_list": mgmt_list,
        "content": content,
        "request": request})


@router.get("/dashboard")
def dashboard(request: Request):
    return templates.TemplateResponse(router.prefix+"/dashboard.html", {
        "title":"Dashboard",
        "request": request})


# def dashboard(request):
#     print(cgl.GLOBVAR().myvar)
#     return render(request, "management/dashboard.html", {"title":"Dashboard"})


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
