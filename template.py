from dnacentersdk import DNACenterAPI
import csv
import dnac_credentials


class Template:
    def __init__(self, name, id):
        self.name = name
        self.id = id


def get_pnp_templates(dna_api):
    for project in dna_api.configuration_templates.get_projects():
        if project.name == 'Onboarding Configuration':
            return project.templates


if __name__ == '__main__':

    api = DNACenterAPI(username=dnac_credentials.username,
                       password=dnac_credentials.password,
                       base_url=dnac_credentials.url,
                       version='2.1.2',
                       verify=False)

    pnp_templates = get_pnp_templates(api)
    template_name = input(f'Enter template name {[i.name for i in pnp_templates]}: ')

    for i in pnp_templates:
        if i.name == template_name:
            pnp_template = Template(i.name, i.id)


    params = api.configuration_templates.get_template_details(pnp_template.id).templateParams
    parameters = []
    for param in params:
        if param.required:
            parameters.append(param.parameterName+'*')
        else:
            parameters.append(param.parameterName)

    with open('pnp_params.csv', 'w', newline='') as csvfile:
        fieldnames = ['name', 'serial' ,'top_of_stack', 'pid', 'site_name', 'image','template_name'] + parameters
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({'template_name': pnp_template.name,
                          'image': 'cat9k_iosxe.17.03.03.SPA.bin'})