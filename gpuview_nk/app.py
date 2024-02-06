#!/usr/bin/env python

"""
Web API of gpuview.

@author Fitsum Gaim
@url https://github.com/fgaim
"""

import os
import json
from datetime import datetime
import pytz  
from bottle import Bottle, TEMPLATE_PATH, template, response, request, redirect

import utils
import core, commute



app = Bottle()
abs_path = os.path.dirname(os.path.realpath(__file__))
abs_views_path = os.path.join(abs_path, 'views')
TEMPLATE_PATH.insert(0, abs_views_path)

EXCLUDE_SELF = False  # Do not report to `/gpustat` calls.


@app.route('/')
def index():
    gpustats = core.all_gpustats()
    now = datetime.now().strftime('Updated at %Y-%m-%d %H-%M-%S')
    return template('index', gpustats=gpustats, update_time=now)


@app.route('/gpustat', methods=['GET'])
def report_gpustat():
    """
    Returns the gpustat of this host.
        See `exclude-self` option of `gpuview run`.
    """

    def _date_handler(obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        else:
            raise TypeError(type(obj))

    response.content_type = 'application/json'
    if EXCLUDE_SELF:
        resp = {'error': 'Excluded self!'}
    else:
        resp = core.my_gpustat()
    return json.dumps(resp, default=_date_handler)

@app.route('/apply_reservation', method='POST')
def apply_reservation():
    reservation_data = json.load(request.body)
    print(reservation_data)
    core.apply_reservation(reservation_data)
    gpu_users = core.load_reservations()
    return json.dumps({'gpu_users': gpu_users})

@app.route('/remove_reservation', method='POST')
def remove_reservation():
    reservation_data = json.load(request.body)
    print(reservation_data)
    core.remove_reservation(reservation_data)
    gpu_users = core.load_reservations()
    return json.dumps({'gpu_users': gpu_users})

@app.route('/go_to_work', method='POST')
def go_to_work():
    
    utc_time = datetime.utcnow().replace(tzinfo=pytz.utc)
    kst_time = utc_time.astimezone(pytz.timezone('Asia/Seoul'))
    
    commute_data = json.load(request.body)
    print(commute_data)
    if kst_time.weekday() in range(0, 5) and (kst_time.hour < 8 or (kst_time.hour == 8 and kst_time.minute < 30)):
        result = commute.check_commute(commute_data['id'], commute_data['pw'], 1)
    else:
        result = "출근시간이 아니에용!"
        
    response.content_type = 'application/json'
    return json.dumps(result, ensure_ascii=False)

@app.route('/leave_work', method='POST')
def leave_work():
    
    utc_time = datetime.utcnow().replace(tzinfo=pytz.utc)
    kst_time = utc_time.astimezone(pytz.timezone('Asia/Seoul'))
    
    commute_data = json.load(request.body)
    print(commute_data)
    if kst_time.weekday() in range(0, 5) and 15 <= kst_time.hour < 18:
        result = commute.check_commute(commute_data['id'], commute_data['pw'], 2)
    else:
        result = "퇴근시간이 아니에용!"
    
    response.content_type = 'application/json'
    return json.dumps(result, ensure_ascii=False)

def main():
    parser = utils.arg_parser()
    args = parser.parse_args()

    if 'run' == args.action:
        core.safe_zone(args.safe_zone)
        global EXCLUDE_SELF
        EXCLUDE_SELF = args.exclude_self
        app.run(host=args.host, port=args.port, debug=args.debug)
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
