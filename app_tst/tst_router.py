import yaml
from typing import Dict
from fastapi import APIRouter, WebSocket, Request, BackgroundTasks #, Response #, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from random import randint
import asyncio
import time

from sse_starlette.sse import EventSourceResponse

from include import cpg
from include import cpf
from include.cgl import logger

router = APIRouter(
    prefix="/test",
    tags=["Test"]
)

templates = Jinja2Templates(directory="templates")

message = "MsgInit"
status = "StatusInit"

#region AJAX
# async def tst_action(action=""):
#     global message

#     for i in range(10,20):
#         # message = "<p>Test <strong>" + str(randint(10, 99)) + "</strong> " + action + "</p>"
#         message = "<p>Test <strong>" + str(i) + "</strong> " + action + "</p>"
#         logger.debug(message)
#         await asyncio.sleep(1)
#     # if randint(1,3) == 2:

#     message = ""
#     return

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
    # if action and (get_status is None):
    #     # tst_index.iter_no += 1
    #     # run something
    #     logger.info('Calling test_action')
    #     asyncio.create_task(test_action())
    #     logger.info('Redirecting')
    #     return RedirectResponse("?get_status")

    return templates.TemplateResponse(router.prefix+"/index.html", {
        "title":"Index",
        "content": content,
        "request": request})

# @router.get("/get_status")
# async def tst_get_status(request: Request, action:str=""):

#     # status_updates = []
#     # for i in range(5):
#     #     status_updates.append(f"Processing... Step {i+1}")

#     # return {"status": status_updates}

#     # message = "<p>Test <strong>" + str(randint(10, 99)) + "</strong> " + action + "</p>"
#     # if randint(1,3) == 2:
#     #     message = ""
#     # # for tests
#     # from src import schemas as sch
#     # from include import cpf
#     # res = cpf.Mgmt().fetch_packages_dmn("mdmPrime", dmn="cpGitOps")
#     # status, client = cpf.Mgmt().login(sch.ManagementToLogin(name="mdmPrime", dmn="cpGitOps"))
#     # content=status
#     logger.info(message)
#     return { "message": message }

#endregion AJAX

#region SSE
# @router.get("/init")
# async def get():
#     content = """
#     <html>
#       <body>
#         <a href="/test/start">Start process</a>
#         <div id="status" style="border:1px; padding:2px;">-= Init =-<br/></div>
#         <script>
#             var eventSource = new EventSource("/test/sse");
#             //eventSource.onmessage = function(event) {
#             //  document.getElementById("status").innerHTML += event.data + "<br>";
#             //};

#             eventSource.addEventListener('join', event => {
#             alert(`${event.data} зашёл`);
#             });

#             eventSource.addEventListener('message', event => {
#                 document.getElementById("status").innerHTML += event.data + "<br>";
#             });

#             eventSource.addEventListener('leave', event => {
#             alert(`${event.data} вышел`);
#             });
#         </script>
#       </body>
#     </html>
#     """
#     return HTMLResponse(content=content)


# async def long_running_task():
#     global status
#     for i in range(5):
#         await asyncio.sleep(1)  # Simulate a time consuming task
#         status = f"Task progress: {i+1}"


# # @router.get("/start")
# # async def start(request: Request):
# #     async_generator = request.app.state.sse()
# #     for i in range(5):
# #         time.sleep(1)
# #         await async_generator.asend({"data": f"Iteration {i+1}"})
# #     return {"url": "/test/done"}

# @router.get("/start")
# async def start_task(background_tasks: BackgroundTasks):
#     global status
#     status = "Task started"
#     background_tasks.add_task(long_running_task)
#     # return {"message": "Task started"}
#     return RedirectResponse("/test/init")

# # @router.get("/done")
# # async def done():
# #     return {"message": "Process complete!"}


# @router.get("/sse")
# async def sse(request: Request):
#     async def stream():
#         global status
#         print("~")
#         while True:
#             # data = yield
#             # yield {"data": data}
#             print(status, end=" ")
#             if status != "-":
#                 yield f"data: {status}"
#                 status = "-"
#             await asyncio.sleep(1)

#     print("=")
#     request.app.state.sse = stream()
#     return EventSourceResponse(request.app.state.sse)
#endregion SSE

#region WS

html = """
<html>
  <body>
    <a href="/test/start">Start process</a>
    <div id="status" style="border:1px; padding:2px;">-= Init =-<br/></div>
    <script>
      var ws = new WebSocket("ws://localhost:8000/test/ws");
      ws.onmessage = function(event) {
        document.getElementById("status").innerHTML += event.data + "<br>";
      }
    </script>
  </body>
</html>
"""

connected_websockets = set()


# async def send_update(websocket, message):
#     await websocket.send_text(message)


# async def perform_action_and_send_updates(websocket):
#     # Simulated action that takes time
#     for i in range(5):
#         await send_update(websocket, f"Processing... Step {i+1}")
#         await asyncio.sleep(2)  # Simulating a delay


# @router.get("/init")
# async def get():
#     print("get")
#     return HTMLResponse(content=html)


# @router.websocket("/ws")
# async def websocket(websocket: WebSocket):
#     print("websocket")
#     await websocket.accept()
#     connected_websockets.add(websocket)
#     try:
#         while True:
#             # data = await websocket.receive_text()
#             # await perform_action_and_send_updates(websocket)
#             await websocket.send_text(f"{message}")
#             await asyncio.sleep(2)  # Check for updates after every 5 seconds
#     except Exception:
#         connected_websockets.remove(websocket)



# @router.get("/start")
# async def start():
#     print("Start")
#     for i in range(5):
#         time.sleep(1)
#         await websocket.send_text(f"Iteration {i+1}")
#     return RedirectResponse("/test/done")


# @router.get("/done")
# async def done():
#     print("Done")
#     return {"message": "Process complete!"}

websockets = []

async def long_running_task(prefix=""):
    global status
    logger.debug(f"long {prefix}")
    await asyncio.sleep(2)
    await send_update({"ws_content": ""})
    for i in range(5):
        status = f"Task progress: {prefix} {i+1}"
        content = f"<p>Content: <strong>{prefix} {i+1}</strong></p>"
        await send_update({"ws_status": status, "ws_content": content})
        await asyncio.sleep(1)  # Simulate a time consuming task
    await send_update({"ws_status": ""})


async def send_update(message:Dict):
    for wait in range(20): # give some time to establish websocket connection
        await asyncio.sleep(0.1)
        if len(websockets) > 0:
            break
    if len(websockets) > 0:
        await websockets[0].send_json(message)
    else:
        logger.error(f"No websocket for {message}")

@router.websocket("/ws")
async def websocket(websocket: WebSocket, background_tasks: BackgroundTasks):
    print("websocket")
    await websocket.accept()
    websockets.append(websocket)
    connected_websockets.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            logger.warning(data)
            # background_tasks.add_task(long_running_task, "2nd")
            await long_running_task("3rd")
            logger.warning("run task")
            # await perform_action_and_send_updates(websocket)
            # await websocket.send_text(f"{data}")
            await asyncio.sleep(1)  # Check for updates after every 5 seconds
    except Exception:
        websockets.remove(websocket)
        connected_websockets.remove(websocket)



@router.get("/show_ws")
async def tst_show_ws(request: Request, background_tasks: BackgroundTasks):
    content = "NoContent"
    background_tasks.add_task(long_running_task, "1st")

    return templates.TemplateResponse(router.prefix+"/show_ws.html", {
        "title":"Show_WS",
        "content": content,
        "request": request})

#endregion WS