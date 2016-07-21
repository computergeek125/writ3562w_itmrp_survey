import http.client as HTC
import json
import os
import shutil
import sys
import tempfile
import threading
import time
import traceback
from urllib.parse import urlparse
import zipfile

from qualtrics_api.QualtricsException import QualtricsException

class Qualtrics_v3():
    def __init__(self, base_uri, api_token):
        self.version = (3)
        self.base_uri = base_uri
        self.token = api_token
        self.api_url = '/API/v3/'
        self.headers = {'X-API-TOKEN': api_token}
    def request(self, method, command, data=None, headers={}): 
        # Primary interface to HTTP client.  Thread safe; initiates one HTTPS connection per operation
        # Returns parsed JSON from Qualtrics
        # Does not raise an exception upon HTTP errors; the calling function is responsible for catching errors
        url_req = "https://{0}/{1}".format(self.base_uri, self.api_url + command)
        return self.request_url(method, url_req, data=data, headers=headers)
    def request_url(self, method, url, data=None, headers={}, raw=False):
        url_parsed = urlparse(url)
        if url_parsed.scheme.lower() != "https":
            sys.stdout.write("WARNING: url scheme is not HTTPS!\n")
        if url_parsed.netloc == "":
            sys.stdout.write("WARNING: could not detect network location!\n")  
        htc = HTC.HTTPSConnection(self.base_uri)
        send_headers = self.headers.copy()
        send_headers.update(headers)
        htc.request(method, url, body=data, headers=send_headers)
        resp = htc.getresponse()
        if raw:
            return resp
        rt = resp.read().decode('UTF-8')
        data = json.loads(rt)
        return {"stat_code":resp.status, "status_msg":resp.reason, "data":data}
    # surveys!
    def survey_list(self):
        raw = self.request("GET", "surveys")
        if raw["stat_code"] != 200:
            raise QualtricsException("Qualtrics error {0} ({1})".format(raw["data"]["meta"]["error"]["errorMessage"], raw["data"]["meta"]["error"]["errorCode"]))
        else:
            data = raw["data"]["result"]["elements"]
            meta = raw["data"]["meta"]
            nextpage = raw["data"]["result"]["nextPage"]
            while(nextpage is not None):
                npr = self.request_url("GET", nextpage)
                npd = npr["data"]["result"]["elements"]
                nextpage = npr["data"]["result"]["nextPage"]
                data += npd
            return data
    def survey_get(self, sid):
        raw = self.request("GET", "surveys/{0}".format(sid))
        if raw["stat_code"] != 200:
            raise QualtricsException("Qualtrics error {0} ({1})".format(raw["data"]["meta"]["error"]["errorMessage"], raw["data"]["meta"]["error"]["errorCode"]))
        else:
            data = raw["data"]["result"]
            meta = raw["data"]["meta"]
            return data

    # response exports!
    def response_export(self, sid, etype):
        start_time = time.time()
        headers = {"Content-Type":"application/json"}
        post = {"surveyId": sid, "format": etype}
        rdoc_raw = self.request("POST", "responseexports", data=json.dumps(post), headers=headers)
        if rdoc_raw["stat_code"] != 200:
            raise QualtricsException("Qualtrics error {0} ({1})".format(raw["data"]["meta"]["error"]["errorMessage"], raw["data"]["meta"]["error"]["errorCode"]))
        rdoc_id = rdoc_raw['data']['result']['id']
        rc_progress = 0
        rc_command = "responseexports/" + rdoc_id
        while rc_progress < 100:
            rc_raw = self.request("GET", rc_command)
            rc_progress = rc_raw['data']['result']['percentComplete']
            print("Download is {0}% processed".format(rc_progress))
        # download and unzip the file
        rdoc_url = rc_raw['data']['result']['file']
        rdoc_req = self.request_url("GET", rdoc_url, raw=True)
        rdoc_zip_name = "qualtrics_{0}_{1}".format(int(start_time), etype)
        rdoc_zip_path = tempfile.gettempdir()+"/"+rdoc_zip_name+".zip"
        try:
            rdoc_size = int(rdoc_req.info().getheader('Content-Length').strip())
        except AttributeError:
            rdoc_size = -1
        rdoc_progress_bytes = 0
        with open(rdoc_zip_path, "wb") as f: #http://stackoverflow.com/a/27971337/1778122
            while True:
                buf = rdoc_req.read(8192)
                if not buf:
                    break
                rdoc_progress_bytes += len(buf)
                f.write(buf)
                if rdoc_size > -1:
                    print("Downloading {0}/{1} MB ({2:.2f})".format(rdoc_progress_bytes/1000, rdoc_size/1000, (rdoc_progress_bytes/rdoc_size*100)))
                else:
                    print("Downloading {0} MB".format(rdoc_progress_bytes/1000))
        print("Download finished to {0}".format(rdoc_zip_path))
        rdoc_unzip_path = tempfile.gettempdir()+"/"+rdoc_zip_name
        zipfile.ZipFile(rdoc_zip_path).extractall(rdoc_unzip_path)
        rdoc_path = rdoc_unzip_path + "/" + os.listdir(rdoc_unzip_path)[0]
        return rdoc_path

    # TODO: cleans up ALL Qualtrics temporary files, not just ones from this session!
    def response_clean(self):
        tmp = tempfile.gettempdir()
        cldir = os.listdir(tmp)
        dm = []
        for i in cldir:
            if i.startswith("qualtrics_"):
                dm += [i]
        for i in dm:
            try:
                fn = tmp+"/"+i
                if os.path.isfile(fn):
                    os.remove(fn)
                elif os.path.isdir(fn):
                    shutil.rmtree(fn)
                else:
                    sys.stderr.write("ERROR: {0} is not a file or directory\n".format(fn))
            except PermissionError:
                traceback.print_exc(file=sys.stderr)
