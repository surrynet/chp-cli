import requests
import json
import os

class Proxy(object):
    '''
    Configurable-HTTP-Proxy 서버의 사용자 API
    CONFIGPROXY_AUTH_TOKEN 은 환경변수로 받아야 함
    '''
    
    url = 'http://proxy:8001/api/routes'
    headers = {}
    path_prefix = None
    data = None
    token = None

    def __init__(self, application):
        self.token = os.environ['CONFIGPROXY_AUTH_TOKEN']
        self.headers['Authorization'] = 'token {token}'.format(token=self.token)
        self.path_prefix = application
    
    def status(self):
        '''
        Routes에서 '/<application>' prefix를 갖는 path 조회 
        '''
        ret = {}
        res = requests.get(self.url, headers=self.headers)
        for k, v in res.json().items():
            if k.startswith(self.path_prefix):
                ret[k] = v
        return ret
    
    def remove(self, path):
        '''
        Routes에서 '/<application>' prefix를 갖는 path 삭제
        '''
        url = self.url + self.path_prefix + '/' + path
        res = requests.delete(url, headers=self.headers)
        return res
    
    def create(self, path, proxy_url):
        '''
        Routes에 '/<application>' prefix를 갖는 path를 추가
        '''
        target_path = self.path_prefix + '/' + path
        url = self.url + target_path
        data = {'target': proxy_url}
        res = requests.post(url, headers=self.headers, data=json.dumps(data))
        return res
