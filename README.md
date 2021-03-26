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