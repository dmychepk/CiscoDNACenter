from flask import Flask, render_template, request, Response
from concurrent.futures import ThreadPoolExecutor
from dnacentersdk import DNACenterAPI
from itertools import repeat
import time
import urllib3


class Device:
    def __init__(self, hostname, ipAddress, dictionary):
        self.hostname = hostname
        self.ipAddress = ipAddress
        self.add_device_status = None
        self.site_id = None
        for k, v in dictionary.items():
            setattr(self, k, v)


urllib3.disable_warnings()


api = DNACenterAPI()


app = Flask(__name__)


@app.route("/", methods = ["POST", "GET"])
def home():
    if request.method == "POST":

        parameters = {'userName': request.form["userName"],
                      'password': request.form["password"],
                      'enablePassword': request.form["enablePassword"],
                      'cliTransport': request.form["cliTransport"],
                      'type': 'NETWORK_DEVICE',
                      'snmpVersion': 'v2',
                      'snmpRetry': 3,
                      'snmpTimeout': 5,
                      'snmpROCommunity': request.form["snmpROCommunity"],
                      'snmpRWCommunity': request.form["snmpRWCommunity"],
                      'active_validation': False}

        list_of_devices = request.form["devices"]
        devices = []
        for device in list_of_devices.split():
            hostname, ip = device.split(',')
            devices.append(Device(hostname,ip,parameters))
        return Response(generate(devices), mimetype='text')
    else:
        return render_template("index.html")


def generate(devices):
    with ThreadPoolExecutor(max_workers=25) as executor:
        result = executor.map(add_device, devices, repeat(api))
        for outcome in result:
            yield outcome


def add_device(device, api):
    call_add_device = api.devices.add_device(ipAddress=[device.ipAddress],
                                 userName=device.userName,
                                 password=device.password,
                                 enablePassword=device.enablePassword,
                                 cliTransport=device.cliTransport,
                                 type=device.type,
                                 snmpVersion=device.snmpVersion,
                                 snmpRetry=device.snmpRetry,
                                 snmpTimeout=device.snmpTimeout,
                                 snmpROCommunity=device.snmpROCommunity,
                                 snmpRWCommunity=device.snmpRWCommunity,
                                 active_validation=device.active_validation)
    time.sleep(30)

    task_tree = api.task.get_task_tree(task_id=call_add_device.response.taskId)
    if not task_tree.response[-1].isError:
        device.add_device_status = task_tree.response[-1].message
    else:
        device.add_device_status = task_tree.response[-1].failureReason

    buildings = api.sites.get_site(type='building').response
    for building in buildings:
        if building.name.split('-')[0] in device.hostname:
            device.site_id = building.id

    if device.site_id:
        site_assignment = api.sites.assign_device_to_site(device.site_id, device=[{"ip": device.ipAddress}], headers={"__runsync": True})
        sar = site_assignment.result.progress
    else:
        device.site_id = "No site found"
        sar = "N/A"

    return f'{device.hostname} | {device.ipAddress} | {device.add_device_status} | {device.site_id} | {sar}\n'


if __name__ == '__main__':

    app.run()