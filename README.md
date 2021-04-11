# Add network devices to Cisco DNA Center and assign them to sites

Set credentials as environment variables:
- DNA_CENTER_VERSION=2.1.2
- DNA_CENTER_USERNAME
- DNA_CENTER_PASSWORD
- DNA_CENTER_BASE_URL
- DNA_CENTER_VERIFY

Run add_devices.py and open http://127.0.0.1:5000/

Provide credentials for devices

Provide list of devices, one device per row in format:
`hostname1,IP address1`
`hostname2,IP address2`

# DNA Center PnP

Enter DNA Center username, password and url into dnac_credentials.py

Run template.py to generate CSV file with input parameters based on chosen day0 template.

Run pnp.py to perform PnP add+claim proccess based on your modified pnp_params.csv file
