import uvicorn
from src.main import app

if __name__ == "__main__":
    dev = 0
    if dev==0:
        #use this one
        uvicorn.run(app, host="127.0.0.1", port=8000,
                    log_level="debug", log_config="src/log_conf.yaml")
    # if dev == 1:
    #     #or this one
    #     uvicorn.run('app.main:api', host="127.0.0.1", port=5000,
    #                 log_level="info", reload=True, debug=True)
    # if dev == 2:
    #     uvicorn.run('app.main:api', host="127.0.0.1", port=5000,
    #                 log_level="info", workers=2)
