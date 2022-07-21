from fastapi import FastAPI
import uvicorn
from fastapi.responses import JSONResponse

from base.register import Register
from base.report import Report
from models.models import Namespace, ReportModel
from base.process import controller


app = FastAPI()


# @app.on_event("startup")
@app.post("/control/start")
async def start():
    msg = controller("start")
    return JSONResponse(status_code=202, content=msg)


@app.post("/control/stop")
async def start():
    msg = controller("stop")
    return JSONResponse(status_code=202, content=msg)


@app.post("/register/")
async def create_item(namespace: Namespace):
    try:
        namespace = dict(namespace)
        reg_obj = Register()
        reg_obj.register_new_namespace(namespace)
        return JSONResponse(status_code=201, content='namespace registered')
    except Exception as e:
        return JSONResponse(content=str(e))


@app.post("/report/terminal")
async def create_item(rep_model: ReportModel):
    try:
        rep_model = dict(rep_model)
        rep_obj = Report()
        resp = rep_obj.get_terminal_report(rep_model)
        return JSONResponse(status_code=200, content=resp)
    except Exception as e:
        return JSONResponse(content=str(e))


@app.post("/report/environment")
async def create_item(rep_model: ReportModel):
    try:
        rep_model = dict(rep_model)
        rep_obj = Report()
        resp = rep_obj.get_env_report(rep_model)
        return JSONResponse(status_code=200, content=resp)
    except Exception as e:
        return JSONResponse(content=str(e))

if __name__ == "__main__":
    uvicorn.run("app:app", debug=True, port=30001)
