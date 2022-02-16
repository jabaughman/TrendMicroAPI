"""
Please update logfeeder.ini configuration.
This script could access log feeder api to
    1. subscribe
    2. get download url links
    3. download files

Example: 
    python subscribe.py
    python query_logs.py

    python subscribe.py --unsubscribe
"""
import json
import os
import sys
import base64
import time
from array import array
import urllib
import urllib2
import time
import datetime
import calendar
import pytz
from ConfigParser import SafeConfigParser
from contextlib import closing

import requests
from Crypto.PublicKey import RSA

from cspi_connection import CSPIConnection


class LogFeeder(object):

    def __init__(self):
        parser = SafeConfigParser()
        parser.read('logfeeder.ini')
        self.ACCESS_TOKEN = parser.get('cspi', 'ACCESS_TOKEN')
        self.SECRET_KEY = parser.get('cspi', 'SECRET_KEY')
        self.SERVER_HOSTNAME = parser.get('cspi', 'SERVER_HOSTNAME')
        self.SERVER_PORT = parser.get('cspi', 'SERVER_PORT')
        self.SUBSCRIBE_URI = "/SMPI/service/wfbss/customer/api/1.0/logfeeder/subscribe"
        self.QUERYLOG_URI  = "/SMPI/service/wfbss/customer/api/1.0/logfeeder/query_logs"
        
        self.public_pem_path = parser.get('logfeeder', 'public_file_path')
        try:
            self.password = parser.get('logfeeder', 'password')
        except:
            print "Please do not use special char like % in password."
            raise
        self.log_types = parser.get('logfeeder', 'log_types').split(',')
        self.storage_path = parser.get('logfeeder', 'storage_path')

    def _run(self, method, subscribe_uri, body=None):
        conn = CSPIConnection(self.ACCESS_TOKEN, self.SECRET_KEY, self.SERVER_HOSTNAME, self.SERVER_PORT)
        try:

            res_status, res_data = conn.send_request(method, subscribe_uri, body=body)
            if res_status != 200:
                print "Response status: \n%r", res_status
                print "Response data: \n%r", json.loads(res_data)['message']
        finally:
            conn.close()

        return res_status, res_data

    def _encrypt_password(self, public_pem_file_path, password):
        with open(public_pem_file_path) as f:
            key = f.read()
            public_key = RSA.importKey(key)
        text = public_key.encrypt(password, 4)
        return base64.b64encode(text[0])

    def _download_file(self, url, cid=None):
        urlp = urllib2.urlparse.urlsplit(url)
        p = urlp.path.split('/')
        if cid is None:
            sub_path = [p[3]]
        else:
            p[2] = "{}".format(cid)
            sub_path = p[2:]
        path = os.path.join(self.storage_path, *sub_path)
        dir_name = os.path.dirname(path)
        local_file = os.path.join(dir_name, p[-1])

        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print "create directory: ", dir_name

        print "start download: ", local_file
        with closing(requests.get(url, stream=True)) as r:
            with open(local_file, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
        print "download is complete."
        return local_file

    def _get_yesterday_time_range(self):
        # get yesterday date
        today = datetime.datetime.now(tz=pytz.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        sec = datetime.timedelta(seconds=1)
        end_datetime = today - sec
        start_datetime = end_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
        start = calendar.timegm(start_datetime.timetuple())
        end = calendar.timegm(end_datetime.timetuple())
        return (start, end)

    def subscribe(self, cid=None):
        log_types = self.log_types
        subscribe = 1
        password  = self._encrypt_password(self.public_pem_path, self.password)
        content = {
            "log_types": log_types,
            "subscribe": subscribe,
            "password" : password,
        }
        if cid is not None:
            uri = self.SUBSCRIBE_URI + "?" + "cids=" + cid
        else:
            uri = self.SUBSCRIBE_URI
        sub_status, sub_data = self._run("POST", uri, json.dumps(content))
        if sub_status == 200:
            print "subscribe successfully."
        else:
            print "subscribe returns error."
        return sub_status, sub_data

    def unsubscribe(self, cid=None):
        subscribe = 0
        content = {
            "subscribe": subscribe,
        }
        if cid is not None:
            uri = self.SUBSCRIBE_URI + "?" + "cids=" + cid
        else:
            uri = self.SUBSCRIBE_URI
        sub_status, sub_data = self._run("POST", uri, json.dumps(content))
        if sub_status == 200:
            print "unsubscribe successfully."
        else:
            print "unsubscribe returns error."
        return sub_status, sub_data

    def query_logs(self, cid=None):
        start_time, end_time = self._get_yesterday_time_range()
        params = {
            'start_time': start_time,
            'end_time'  : end_time,
        }
        if cid is not None:
            params.update({'cids': cid}) 
        uri = self.QUERYLOG_URI + "?"
        for key, value in params.items(): 
            uri += key + "=" + str(value) + "&"
        uri = uri[:-1]

        sub_status, sub_data = self._run("GET", uri)
        if sub_status == 200:
            res_json = json.loads(sub_data)
            if start_time == res_json['last_record']:
                print "The log archive is not finished yet."
                return
            for url in res_json['files']:
                self._download_file(url, cid=cid)
            print "query_logs successfully."
        else:
            print "query_logs return error."
        return sub_status, sub_data
