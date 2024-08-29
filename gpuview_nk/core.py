"""
Core functions of gpuview.

@author Fitsum Gaim
@url https://github.com/fgaim
"""

import ast
import os
import json
import subprocess, time
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

ABS_PATH = os.path.dirname(os.path.realpath(__file__))
HOSTS_DB = os.path.join(ABS_PATH, 'gpu_hosts.db')
RESERVATION_DB = os.path.join(ABS_PATH, 'gpu_reservations.db')
SAFE_ZONE = False  # Safe to report all details.


def safe_zone(safe=False):
    global SAFE_ZONE
    SAFE_ZONE = safe


def my_gpustat():
    """
    Returns a [safe] version of gpustat for this host.
        # See `--safe-zone` option of `gpuview start`.
        # Omit sensitive details, eg. uuid, username, and processes.
        # Set color flag based on gpu temperature:
            # bg-warning, bg-danger, bg-success, bg-primary

    Returns:
        dict: gpustat
    """

    try:
        from gpustat import GPUStatCollection
        stat = GPUStatCollection.new_query().jsonify()
        delete_list = []
        for gpu_id, gpu in enumerate(stat['gpus']):
            if type(gpu['processes']) is str:
                delete_list.append(gpu_id)
                continue
            gpu['memory'] = round(float(gpu['memory.used']) /
                                  float(gpu['memory.total']) * 100)
            if SAFE_ZONE:
                gpu['users'] = len(set([p['username']
                                        for p in gpu['processes']]))
                user_process = [
                    '%s(%s,%sM)' % (p['username'],
                                    p['command'], p['gpu_memory_usage'])
                    for p in gpu['processes']
                ]
                gpu['user_processes'] = ' '.join(user_process)
            else:
                gpu['users'] = len(set([p['username']
                                        for p in gpu['processes']]))
                processes = len(gpu['processes'])
                gpu['user_processes'] = '%s/%s' % (gpu['users'], processes)
                gpu.pop('processes', None)
                gpu.pop("uuid", None)
                gpu.pop("query_time", None)

            gpu['flag'] = 'bg-primary'
            if gpu['temperature.gpu'] > 75:
                gpu['flag'] = 'bg-danger'
            elif gpu['temperature.gpu'] > 50:
                gpu['flag'] = 'bg-warning'
            elif gpu['temperature.gpu'] > 25:
                gpu['flag'] = 'bg-success'

        if delete_list:
            for gpu_id in delete_list:
                stat['gpus'].pop(gpu_id)

        return stat
    except Exception as e:
        return {'error': '%s!' % getattr(e, 'message', str(e))}


def all_gpustats():
    gpustats = []
    hosts = load_hosts()
    reservations = load_reservations()
    try:
        with open('gpustats.json', 'r') as f:
            gpustats = json.load(f)
    except FileNotFoundError:
        print("File not found. Returning empty list.")
    
    try:
        sorted_gpustats = sorted(gpustats, key=lambda g: g['hostname'])
        result_sorted_gpustats = []
        for gpustats in sorted_gpustats:
            if gpustats['hostname'] in  reservations:
                gpustats['user_info']=reservations[gpustats['hostname']]
            result_sorted_gpustats.append(gpustats)
            
        if result_sorted_gpustats is not None:
            return result_sorted_gpustats
        if sorted_gpustats is not None: return sorted_gpustats
    except Exception as e:
        print("Error: %s" % getattr(e, 'message', str(e)))
    return gpustats

    
def load_hosts():

    hosts = {}
    if not os.path.exists(HOSTS_DB):
        print("There are no registered hosts! Use `gpuview add` first.")
        return hosts

    for line in open(HOSTS_DB, 'r'):
        try:
            name, url = line.strip().split('\t')
            hosts[url] = name
        except Exception as e:
            print('Error: %s loading host: %s!' %
                  (getattr(e, 'message', str(e)), line))
    return hosts


def save_hosts(hosts):
    with open(HOSTS_DB, 'w') as f:
        for url in hosts:
            f.write('%s\t%s\n' % (hosts[url], url))


def add_host(url, name=None):
    url = url.strip().strip('/')
    if name is None:
        name = url
    hosts = load_hosts()
    hosts[url] = name
    save_hosts(hosts)
    print('Successfully added host!')

def remove_host(url):
    hosts = load_hosts()
    if hosts.pop(url, None):
        save_hosts(hosts)
        print("Removed host: %s!" % url)
    else:
        print("Couldn't find host: %s!" % url)


def print_hosts():
    hosts = load_hosts()
    if len(hosts):
        hosts = sorted(hosts.items(), key=lambda g: g[1])
        print('#   Name\tURL')
        for idx, host in enumerate(hosts):
            print('%02d. %s\t%s' % (idx+1, host[1], host[0]))

def print_reservations():
    hosts = load_hosts()
    if len(hosts):
        hosts = sorted(hosts.items(), key=lambda g: g[1])
        print('#   Name\tURL')
        for idx, host in enumerate(hosts):
            print('%02d. %s\t%s' % (idx+1, host[1], host[0]))

def install_service(host=None, port=None,
                    safe_zone=False, exclude_self=False):
    arg = ''
    if host is not None:
        arg += '--host %s ' % host
    if port is not None:
        arg += '--port %s ' % port
    if safe_zone:
        arg += '--safe-zone '
    if exclude_self:
        arg += '--exclude-self '
    script = os.path.join(ABS_PATH, 'service.sh')
    subprocess.call('{} "{}"'.format(script, arg.strip()), shell=True)


def load_reservations():
    reservation_dict = {}
    if not os.path.exists(RESERVATION_DB):
        print("There are no registered users! Use `users add` first.")
        return reservation_dict

    for line in open(RESERVATION_DB, 'r'):
        line = line.strip()
        if not line:
            continue  # 비어 있는 라인 건너뛰기

        try:
            server, gpu_reservation = line.split('\t')
            # 따옴표를 큰따옴표로 바꿉니다.
            gpu_reservation = gpu_reservation.replace("'", '"')
            gpu_reservation = json.loads(gpu_reservation)
            reservation_dict[server] = gpu_reservation
        except Exception as e:
            print('Error: %s loading host: %s!' %
                (getattr(e, 'message', str(e)), line))
    return reservation_dict
    
            
            
def save_reservations(new_reservation_data):
    with open(RESERVATION_DB, 'w') as f:
        for server in new_reservation_data:
            f.write('%s\t%s\n' % (server, new_reservation_data[server]))

def apply_reservation(new_reservation_data):
    reservation = load_reservations()
    print("이전예약", reservation)
    print("새로운", new_reservation_data)
    for server, reservations in new_reservation_data.items():
        if server in reservation:
            # 기존 서버의 예약 정보 업데이트
            reservation[server].update(reservations)
        else:
            # 새로운 서버의 예약 정보 추가
            reservation[server] = reservations

    # 병합된 예약 정보 저장
    save_reservations(reservation)
    print('Successfully added reservation!')
    return reservation
    
def remove_reservation(remove_reservation_data):
    reservation = load_reservations()
    for server in remove_reservation_data:
        for idx in remove_reservation_data[server]:
            if server in reservation and idx in reservation[server]:
                reservation[server][idx] = {}
                print("Removed reservation server: %s from gpu: %s!" % (server, idx))
            else:
                print("Couldn't find server: %s from gpu: %s!" % (server, idx))
            
    save_reservations(reservation)
    


        
def print_reservations():
    users = load_reservations()
    if len(users):
        users = sorted(users.items(), key=lambda g: g[1])
        print('#   Name\tURL')
        for idx, host in enumerate(users):
            print('%02d. %s\t%s' % (idx+1, host[1], host[0]))