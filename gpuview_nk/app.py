from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
import pytz
import json
import os

import utils
import core, commute

app = FastAPI()

# Jinja2 templates 설정
abs_path = os.path.dirname(os.path.realpath(__file__))
abs_views_path = os.path.join(abs_path, 'views')
templates = Jinja2Templates(directory=abs_views_path)

EXCLUDE_SELF = False  # Do not report to `/gpustat` calls.
@app.get("/")
async def index(request: Request):
    print("접속")
    gpustats = core.all_gpustats()
    now = datetime.now().strftime('/ at %Y-%m-%d %H-%M-%S')
    print(now)
    return templates.TemplateResponse('index.html', {"request": request, "gpustats": gpustats, "update_time": now})

@app.get("/gpustat")
async def report_gpustat():
    if EXCLUDE_SELF:
        resp = {'error': 'Excluded self!'}
    else:
        resp = core.my_gpustat()
    now = datetime.now().strftime('/gpustat at %Y-%m-%d %H-%M-%S')
    print(now)
    return JSONResponse(content=resp)

@app.post("/apply_reservation")
async def apply_reservation(request: Request):
    request_body = await request.body()
    reservation_data = json.loads(request_body)
    print(reservation_data) 
    core.apply_reservation(reservation_data)
    gpu_users = core.load_reservations()
    return JSONResponse(content={'gpu_users': gpu_users})

@app.post("/remove_reservation")
async def remove_reservation(request: Request):
    request_body = await request.body()
    request_body_str = request_body.decode('utf-8')
    reservation_data = json.loads(request_body_str)
    print(reservation_data) 
    core.remove_reservation(reservation_data)
    gpu_users = core.load_reservations()
    return JSONResponse(content={'gpu_users': gpu_users})

@app.post("/go_to_work")
async def go_to_work(request: Request):
    utc_time = datetime.utcnow().replace(tzinfo=pytz.utc)
    kst_time = utc_time.astimezone(pytz.timezone('Asia/Seoul'))
    
    request_body = await request.body()
    commute_data = request_body.decode('utf-8')
    
    if kst_time.weekday() in range(0, 5) and (kst_time.hour < 8 or (kst_time.hour == 8 and kst_time.minute < 30)):
        result = commute.check_commute(commute_data.id, commute_data.pw, 1)
    else:
        result = "출근시간이 아니에용!"
        
    return JSONResponse(content={"result": result})

@app.post("/leave_work")
async def leave_work(request: Request):
    utc_time = datetime.utcnow().replace(tzinfo=pytz.utc)
    kst_time = utc_time.astimezone(pytz.timezone('Asia/Seoul'))
    
    request_body = await request.body()
    commute_data = request_body.decode('utf-8')
    
    if kst_time.weekday() in range(0, 5) and 15 <= kst_time.hour < 18:
        result = commute.check_commute(commute_data.id, commute_data.pw, 2)
    else:
        result = "퇴근시간이 아니에용!"
    
    return JSONResponse(content={"result": result})

def main():
    parser = utils.arg_parser()
    args = parser.parse_args()

    if 'run' == args.action:
        core.safe_zone(args.safe_zone)
        global EXCLUDE_SELF
        EXCLUDE_SELF = args.exclude_self
        import uvicorn
        uvicorn.run(app, host=args.host, port=args.port, debug=args.debug)
    elif 'service' == args.action:
        core.install_service(host=args.host,
                             port=args.port,
                             safe_zone=args.safe_zone,
                             exclude_self=args.exclude_self)
    elif 'add' == args.action:
        core.add_host(args.url, args.name)
    elif 'remove' == args.action:
        core.remove_host(args.url)
    elif 'hosts' == args.action:
        core.print_hosts()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
