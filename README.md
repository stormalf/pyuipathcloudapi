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

        https://cloud.uipath.com/myorg/mytenant/orchestrator_/odata/Machines

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

if no parameter is defined the default api is called :

    GET /api/Status/Get : check the status of the orchestrator api

        ./pyuipathcloudapi.py
        {"Code": 200, "Reason": "OK"}

some apis need a token to be called and in this case you can add -g parameter to generate the token :

    GET /odata/Machines : get the list of machines

    ./pyuipathcloudapi.py -a /odata/Machines -g

    {'@odata.context': 'https://cloud.uipath.com/myorg/mytenant/orchestrator_/odata/$metadata#Machines/UiPath.Server.Configuration.OData.ExtendedMachineDto', '@odata.count': 1, \
    'value': [{'@odata.type': '#UiPath.Server.Configuration.OData.ExtendedMachineDto', 'LicenseKey': None, 'Name': "your_email's workspace machine", 'Description': None, 'Type': \
    'Template', 'Scope': 'PersonalWorkspace', 'NonProductionSlots': 0, 'UnattendedSlots': 0, 'HeadlessSlots': 0, 'TestAutomationSlots': 0, 'AutomationCloudSlots': 0, \
    'Key': 'zzzzzzzz-z999-9999-9999-zzzzzzzzzzzz', 'AutoScalingProfile': None, 'AutomationType': 'Any', 'TargetFramework': 'Any', 'ClientSecret': None, 'Id': 9999999, \
        'RobotVersions': [], 'RobotUsers': [], 'UpdatePolicy': None, 'Tags': [], 'MaintenanceWindow': None}]}


    POST /odata/Roles : create a new role

    ./pyuipathcloudapi.py -a /odata/Roles -g -J role.json -m POST
    {'message': 'Error : 201 Created'}

    PUT /odata/Roles({id}) : update a role seems not to work for now something special to handle.


    DELETE /odata/Roles({id}) : delete a role

    ./pyuipathcloudapi.py -a "/odata/Roles(99999999)" -g -m DELETE
    {}


    PATCH /odata/Users({id}) : update partially an user information

    ./pyuipathcloudapi.py -a "/odata/Users(9999999)" -g -m PATCH -J user_patch.json
    {"Code": 200, "Reason": "OK"}

## known issues

For now I have some issues with PUT that seems to not work even using curl (not found the correct way to update an existing role).
The PATCH method returns 200 success but no modification taken in account ? but we can see the last modification date updated!

## TODO

- testing all the parameters
- split into two modules one for generating the token and one for executing using the token generated previously ?
- add a parameter to generate the token and store it in a file .env ? and using this token to call the api ?
