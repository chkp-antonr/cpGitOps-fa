from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates

from include.cgl import logger

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
def add_host(request: Request):
    if request.method == "POST":
        logger.debug(f"{request.POST}")
    #     form = frm_add_host(request.POST)
    #     if form.is_valid():
    #         logger.debug(f"Valid form {form.cleaned_data}")
    #         # "add-host" in request.POST to check submit buttin
    #         # return redirect("dwitter:dashboard") to avoid duplications
    #     else:
    #         for field_name, field_err in form.errors.as_data().items():
    #             error = str(list(field_err)[0]).split("'")[1]
    #             logger.warning(f"{field_name}: '{request.POST[field_name]}' - {error}")
    # else:
    #    form = frm_add_host()
    return templates.TemplateResponse(router.prefix+"/add_host.html", {
        "title": "Add host", "request": request})
    # return render(request, "ticket/add-host.html", { "form": form})
