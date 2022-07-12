#!/usr/bin/python3
# -*- coding: utf-8 -*-
from cryptography.fernet import Fernet
import requests
from json import loads as jsonload
import argparse
import os

'''
pyuipathcloudapi.py is to be used by other python modules to automate uipath cloud orchestrator api usage.
it could be called in command line.
See uipath cloud official references to get the correct Api URL and method to use : https://docs.uipath.com/orchestrator/reference/api-references 

Examples:

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
    
'''

__version__ = "1.0.0"

ALLOWED_METHODS = ["DELETE", "GET", "POST", "PUT", "PATCH"]
URL = "https://cloud.uipath.com"
NO_CONTENT = 204
HEADER_JSON = "application/json"
ORCHESTRATOR = "orchestrator_"

def pyuipathcloudApiVersion():
    return f"pyuipathcloudapi version : {__version__}"




class uipathcloudApi():
    def __init__(self, api, method, url,  token, jsonfile, unit, tenant):
        self.api = api
        self.method = method
        self.json = jsonfile
        self.url = url
        if token == None:
            self.token = None
        else:
            self.token = uipathcloudApi.crypted(token)
        self.unit = unit
        self.tenant = tenant


    def __repr__(self):
        return (f"uipathcloudApi api: {self.api}, method: {self.method}, url: {self.url}")

    #return the encrypted password/token
    @classmethod
    def crypted(cls, token):
        cls.privkey = Fernet.generate_key()        
        cipher_suite = Fernet(cls.privkey)
        ciphered_text = cipher_suite.encrypt(token.encode())
        cls.token = ciphered_text
        return cls.token

    #return the decrypted password/token
    @classmethod
    def decrypted(cls, token):
        cls.token = token
        cipher_suite = Fernet(cls.privkey)
        decrypted_text = cipher_suite.decrypt(cls.token)
        decrypted_text = decrypted_text.decode()
        return decrypted_text

    #execute the uipathcloud api using a temp instance
    @staticmethod
    def runuipathcloudApi(api, method, url, token, json, unit, tenant):
        tempuipathcloud = uipathcloudApi(api, method, url, token, json, unit, tenant)
        response = tempuipathcloud.uipathcloudAuthentication()
        tempuipathcloud = None
        return response       


    #egenerate a token
    @staticmethod
    def generatetoken(tenantname, json):
        api = "/oauth/token"
        url = "https://account.uipath.com"
        response = "{}"
        if json == None:
            response = jsonload('{"message": "Error : uipath file  missing! define at least UIPATH_FILE environment variable"}')
            return response 
        if tenantname == None:
            response = jsonload('{"message": "Error : tenant name missing!" define at least UIPATH_TENANTNAME environment variable"}')
            return response             
        try:
            apiurl = url + api  
            header = {}
            header['Accept'] = HEADER_JSON
            header['Content-Type'] = HEADER_JSON     
            header['X-UIPATH-TenantName'] = tenantname 
            contents = open(json, 'rb')
            response = requests.post(apiurl, headers=header, data=contents)
            #print(response)
            contents.close()       
        except requests.exceptions.RequestException as e:  
            raise SystemExit(e)   
        if response.status_code == NO_CONTENT:
            response = "{}"
        elif response.status_code != 200:
            response = jsonload('{"message": "Error : ' + str(response.status_code) + ' ' + response.reason + '"}')
        else:            
            response = response.json()    
            #print(response)                 
        return response       


    #call private function
    def uipathcloudAuthentication(self):
        response = self.__uipathcloudTokenAuth()
        return response

    #internal function that formats the url and calls the uipathcloud apis
    def __uipathcloudTokenAuth(self):
        apiurl = self.url + '/' + self.unit + '/' + self.tenant + '/' + ORCHESTRATOR + self.api  
        header = {}
        header['Accept'] = HEADER_JSON
        # if self.unit != None:
        #     header['X-UIPATH-OrganizationUnitId'] = self.unit  
        if self.token != None:       
            header['Authorization'] = "Bearer " + uipathcloudApi.decrypted(self.token)  
        response = self.__uipathcloudDispatch(apiurl,  header)
        return response

    #internal function that calls the requests
    def __uipathcloudDispatch(self, apiurl,  header):
        response = "{}"        
        try:
            if self.method == "POST":
                contents = open(self.json, 'rb')
                header['Content-Type'] = HEADER_JSON
                response = requests.post(apiurl, headers=header, data=contents)
                contents.close()
            elif self.method == "GET":
                response = requests.get(apiurl,  headers=header)
            elif self.method == "PUT":
                if self.json == '':
                    response = requests.put(apiurl,  headers=header)
                else:
                    contents = open(self.json, 'rb') 
                    header['Content-Type'] = HEADER_JSON     
                    response = requests.put(apiurl,  headers=header, data=contents)
                    contents.close()
            elif self.method == "PATCH":
                if self.json == '':
                    response = requests.patch(apiurl,  headers=header)
                else:
                    contents = open(self.json, 'rb') 
                    header['Content-Type'] = HEADER_JSON     
                    response = requests.patch(apiurl,  headers=header, data=contents)
                    contents.close()                    
            elif self.method == "DELETE":
                #raise Exception("DELETE not implemented yet")
                response = requests.delete(apiurl,  headers=header)  
        except requests.exceptions.RequestException as e:  
            raise SystemExit(e)   
        if response.status_code == NO_CONTENT:
            response = "{}"
        elif response.status_code != 200:
            response = jsonload('{"message": "Error : ' + str(response.status_code) + ' ' + response.reason + '"}')
        else:        
            #print(response.headers)    
            try:
                response = response.json()
            except :
                response = '{"Code": ' + str(response.status_code) + ', "Reason": "' + response.reason + '"}'  
        return response

def pyuipathcloudapi(args):
    message = ''
    if args.tenantname == '':
        itenantname = os.environ.get("UIPATH_TENANTNAME")
    else:
        itenantname = args.tenantname
    if itenantname == None:
        return {"Error": "tenant name missing! define at least UIPATH_TENANTNAME environment variable"}
    if args.unit == '':
        iunit = os.environ.get("UIPATH_UNIT")
    else:
        iunit = args.unit    
    if iunit == None:
        return  {"Error": "Error : unit missing! define at least UIPATH_UNIT environment variable"}     
    if args.api == '' and args.jsonfile == '':
        api="/api/Status/Get"
    else:
        api=args.api    
    if args.url == '':
        iurl = URL
    else:
        iurl = args.url        
    method = args.method     
    if "POST" in method and args.jsonfile == "":
        return {"Error": "Json file required with method POST!"}
    json = args.jsonfile  
    if args.uipathfile == '':
        uipathfile = os.environ.get("UIPATH_FILE")
    else:
        uipathfile = args.uipathfile
    #generate a token first and use this token to call the api.
    if args.generatetoken == True:
        if uipathfile == None:
            return {"Error": "uipath file missing! define at least UIPATH_FILE environment variable"}
        message= uipathcloudApi.generatetoken(tenantname=itenantname, json=uipathfile)
        itoken = message['access_token']
    else:
        itoken = None
    message= uipathcloudApi.runuipathcloudApi(api=api, method=method, url=iurl, token=itoken, json=json, unit=iunit, tenant=itenantname) 
    return message


if __name__== "__main__":
    helpmethod = f"should contain one of the method to use : {str(ALLOWED_METHODS)}"
    parser = argparse.ArgumentParser(description="pyuipathcloudapi is a python3 program that call uipath cloud apis in command line or imported as a module")
    parser.add_argument('-V', '--version', help='Display the version of pyuipathcloudapi', action='version', version=pyuipathcloudApiVersion())
    parser.add_argument('-U', '--unit', help='uipathcloud organization unit id', default='', required=False)    
    parser.add_argument('-T', '--tenantname', help='uipathcloud tenant name', default='', required=False)            
    parser.add_argument('-F', '--uipathfile', help='uipathcloud file needed to generate token', default='', required=False)    
    parser.add_argument('-u', '--url', help='uipathcloud url', default='', required=False)    
    parser.add_argument('-a', '--api', help='uipathcloud api should start by a slash', default='', required=False)    
    parser.add_argument('-m', '--method', help = helpmethod, default="GET", required=False)   
    parser.add_argument('-J', '--jsonfile', help='json file needed for POST method', default='', required=False)
    parser.add_argument('-g', '--generatetoken', help='generate token first before calling API', action="store_true" , required=False)    
    args = parser.parse_args()
    message = pyuipathcloudapi(args)
    print(message)