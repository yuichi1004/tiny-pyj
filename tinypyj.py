# Copyright (C) 2014 Yuichi Murata
# https://github.com/yuichi1004/tiny-pyj
import re
import json
import urllib2
import urllib
import base64

class RpcMethod(object):
    def __init__(self, client, method, service):
        self.service = service 
        self.method = method
        self.client = client
    def __call__(self, *args, **kwargs):
        return self.client.request(self.method, self.service, args, kwargs)

class RpcError(Exception): 
    def __init__(self, msg):
        super(RpcError, self).__init__(msg)

class RpcValidationError(RpcError): 
    def __init__(self, msg):
        super(RpcValidationError, self).__init__(msg)

class Client(object):
    def __init__(self, smd, host, username = None, password = None):
        self.smd = smd
        self.host = host
        self.username = username
        self.password = password
        self.services = smd['services']
        for s in self.services:
            method_name = re.sub('([A-Z])', r'_\1', s).lower()
            setattr(self, method_name, RpcMethod(self, s, self.services[s]))
        
        self.url_opener = urllib2.build_opener()
        if username is not None and password is not None:
            password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
            password_mgr.add_password(None, self.host, username, password)
            auth_handler = urllib2.HTTPBasicAuthHandler(password_mgr)
            self.url_opener = urllib2.build_opener(auth_handler)
    
    def validate_param(self, name, value, type):
        if (type == 'integer'):
            if not isinstance(value, int):
                raise RpcValidationError('{} needs to be integer'.format(name))
        if (type == 'string'):
            if not isinstance(value, str):
                raise RpcValidationError('{} needs to be string'.format(name))
        if (type == 'boolean'):
            if not isinstance(value, bool):
                raise RpcValidationError('{} needs to be boolean'.format(name))

    def request(self, method, service, args, kwargs):
        unchecked_args = kwargs
        checked_args = {}
        parameters = service['parameters']
        for i in range(0, len(args)):
            name = parameters[i]['name']
            unchecked_args[name] = args[i]
        for p in parameters:
            name = p['name']
            if name in unchecked_args:
                self.validate_param(name, unchecked_args[name], p['type'])
                checked_args[name] = unchecked_args[name]
                del unchecked_args[name]
            else:
                if not p['optional']:
                    raise RpcError('arg {} is required'.format(name))
        if len(unchecked_args) > 0:
            raise RpcError('Unknown args: ' + str(unchecked_args))

        transport = self.smd['transport']
        if 'transport' in service:
            transport = service['transport']
        
        headers = {'content-type': 'application/json'}
        payload = {
            'method': method,
            'jsonrpc': '2.0',
            'id': 1,
        }
        
        url = self.host + self.smd['target']
        req = None
        if transport == 'POST':
            if (checked_args is not None):
                payload['params'] = checked_args 
            req = urllib2.Request(url, json.dumps(payload), headers)
        elif transport == 'GET':
            if (checked_args is not None):
                paramstr = json.dumps(checked_args)
                paramstr =  base64.b64encode(paramstr)
                payload['params'] = paramstr
            query = urllib.urlencode(payload)
            req = urllib2.Request(url + '?' + urllib.urlencode(payload),
                    None, headers)
        else:
            raise RpcError('Unknown transport: ' + transport)
        resp = None
        try:
            resp = self.url_opener.open(req)
        except urllib2.URLError, e:
            resp = e
        j = json.loads(resp.read())
        if ('error' in j):
            raise RpcError(j['error'])
        return j['result']

