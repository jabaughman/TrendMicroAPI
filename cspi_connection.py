import base64
import calendar
import hashlib
import hmac
import httplib
import time
import uuid


class CSPIConnection(object):
    def __init__(self, access_token, secret_key, hostname, port, timeout=30):
        self.access_token = access_token
        self.secret_key = secret_key
        self.hostname = hostname
        self.port = port
        self.timeout = timeout

        self.connect()

    def __del__(self):
        self.close()

    def connect(self):
        if int(self.port) == 443:
            self.conn = httplib.HTTPSConnection(self.hostname, self.port,
                                                timeout=self.timeout)
        else:
            self.conn = httplib.HTTPConnection(self.hostname, self.port,
                                               timeout=self.timeout)

    def send_request(self, http_method, request_uri, body=None):
        '''
        Send request to access CSPI
        '''
        headers = get_auth_headers(self.access_token, self.secret_key,
                                   http_method, request_uri, body)
        self.conn.request(http_method, request_uri, body, headers)
        resp = self.conn.getresponse()
        return (resp.status, resp.read())

    def close(self):
        self.conn.close()


def get_auth_headers(access_token, secret_key, method, request_uri, body):
    '''
    Generate authentication herders
    '''
    posix_time = calendar.timegm(time.gmtime())

    headers = {}
    headers["content-type"] = "application/json"
    headers["x-access-token"] = access_token
    headers["x-signature"] = \
        gen_x_signature(secret_key, str(posix_time),
                        method, request_uri, body)
    headers["x-posix-time"] = posix_time
    headers["x-traceid"] = str(uuid.uuid4())

    return headers


def gen_x_signature(secret_key, x_posix_time, request_method, request_uri,
                    body):
    '''
    Generate x-signature
    '''
    payload = x_posix_time + request_method.upper() + request_uri
    if body:
        payload += get_content_md5(body)
    hm = hmac.new(secret_key.encode("utf8"),
                  payload.encode("utf8"), hashlib.sha256)
    digest = hm.digest()
    digest = base64.b64encode(digest)
    return digest


def get_content_md5(content):
    '''
    Get hashed content
    '''
    m = hashlib.md5()
    m.update(content)
    digest = m.digest()
    digest = base64.b64encode(digest)

    return digest
