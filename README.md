# pyuipathcloudapi

python3 api to connect to uipath cloud orchestrator.

Not sure to keep it as the other apis modules that I created.
The main issue here is that we need to generate a token and you can use it for some time after you need to regenerate a new one.
For now, I decided to add a parameter -g to generate the token and in this case the token is used to access to the API.

The difficulty here is we need : one url to generate the token and one other to access to the APi using the token generated.

## api url

the api url is build with :

    "https://cloud.uipath.com" + '/' + your_organization_unit + '/' + your_tenant_name + '/' + "orchestrator_" + endpoint_api

    example :

        https://cloud.uipath.com/myorg/mytenant/orchestrator_api/odata/Machines

## environment variables

UIPATH_UNIT=your_organization_unit
UIPATH_TENANTNAME=your_tenant_name
UIPATH_FILE=your_uipath_file

The content of UIPATH_FILE :

{
"grant_type": "refresh_token",
"client_id": "{your_client_id}",
"refresh_token": "{your_user_key}"
}

## usage

./pyuipathcloudapi.py --help

    usage: pyuipathcloudapi.py [-h] [-V] [-U UNIT] [-T TENANTNAME] [-F UIPATHFILE] [-u URL] [-a API] [-m METHOD]
                            [-J JSONFILE] [-g]

    pyuipathcloudapi is a python3 program that call uipath cloud apis in command line or imported as a module

    optional arguments:
    -h, --help            show this help message and exit
    -V, --version         Display the version of pyuipathcloudapi
    -U UNIT, --unit UNIT  uipathcloud organization unit id
    -T TENANTNAME, --tenantname TENANTNAME
                            uipathcloud tenant name
    -F UIPATHFILE, --uipathfile UIPATHFILE
                            uipathcloud file needed to generate token
    -u URL, --url URL     uipathcloud url
    -a API, --api API     uipathcloud api should start by a slash
    -m METHOD, --method METHOD
                            should contain one of the method to use : ['DELETE', 'GET', 'POST', 'PUT']
    -J JSONFILE, --jsonfile JSONFILE
                            json file needed for POST method
    -g, --generatetoken   generate token first before calling API

## example

    ./pyuipathcloudapi.py -a /odata/Machines -g

## TODO

- testing all the parameters
- split into two modules one for generating the token and one for executing using the token generated previously ?
- add a parameter to generate the token and store it in a file .env ? and using this token to call the api ?
