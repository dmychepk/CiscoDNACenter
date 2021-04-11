import csv
from dnacentersdk import DNACenterAPI
import dnac_credentials

class Device:
    def __init__(self, parameters):
        for k, v in parameters.items():
            setattr(self, k, v)
        self.site_id = None
        self.stack = False
        self.template_id = None
        self.device_id = None
        self.image_id = None

    def get_site_id(self, intent_api):
        self.site_id = intent_api.sites.get_site(name=self.site_name).response[0].id

    def get_stack(self):
        if self.top_of_stack:
            self.stack = True

    def get_template_id(self, intent_api):
        pnp_templates = intent_api.configuration_templates.get_projects(name='Onboarding Configuration')[0].templates
        for template in pnp_templates:
            if template.name == self.template_name:
                self.template_id = template.id

    def get_image_id(self, intent_api):
        self.image_id = intent_api.software_image_management_swim.get_software_image_details(name=self.image).response[0].imageUuid

    def get_params(self, intent_api):
        params = []
        for param in intent_api.configuration_templates.get_template_details(self.template_id).templateParams:
            name = param.parameterName
            params.append({"key": name, "value": self.__dict__[name]})
        return params

if __name__ == '__main__':

    with open('pnp_params.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        devices = []
        for device in reader:
            devices.append(Device(device))

    api = DNACenterAPI(username=dnac_credentials.username,
                       password=dnac_credentials.password,
                       base_url=dnac_credentials.url,
                       version='2.1.2',
                       verify=False)

    for device in devices:

        device.get_site_id(api)
        device.get_stack()
        device.get_template_id(api)
        device.get_image_id(api)
        variables = device.get_params(api)

        # Add Device
        device_add_payload = [{
            "deviceInfo": {
                "hostname": device.name,
                "serialNumber": device.serial,
                "pid": device.pid,
                "stack": device.stack
            }
        }]
        added_device = api.device_onboarding_pnp.import_devices_in_bulk(payload=device_add_payload)
        if added_device['successList']:
            device.device_id = added_device.successList[0].id
        else:
            device.device_id = api.device_onboarding_pnp.get_device_list(serial_number=device.serial)[0].id

        # Claim Device
        device_claim_payload = {
            "siteId": device.site_id,
            "deviceId": device.device_id,
            "type": "Default",
            "imageInfo": {"imageId": device.image_id, "skip": False},
            "configInfo": {"configId": device.template_id,
                           "configParameters": variables}
        }
        if device.stack:
            device_claim_payload["type"] = "StackSwitch"
            device_claim_payload["topOfStackSerialNumber"] = device.top_of_stack
        api.device_onboarding_pnp.claim_a_device_to_a_site(payload=device_claim_payload, active_validation=False)