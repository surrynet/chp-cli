import os
import sys
import getopt
import json
import signal
import socket
from subprocess import getoutput
from threading import Thread

from .proxy import Proxy
from .app import voila, tensorboard

def usage():
    print('''chp-cli [ACTION] [APPLICATION] [ARGUMENT]

configurable-http-proxy의 사용을 단순화한 운영툴
CONFIGPROXY_AUTH_TOKEN, JUPYTERHUB_USER 환경변수가 존재 해햐 한다.

Actions
=======
status
    현재 서비스 중인 application 의 proxy 상태
create
    application instance와 proxy 경로를 생성한다.
remove
    application instance와 proxy 경로를 제거한다.

Application
==========
voila
    * argument: ipynb file
tensorboard
    * argument: logdir directory

Options
=======
-p, --port <Int>
    application instance port
-s, --suffix <String>
    JupyterHub에서 application intance 접근 경로 /<APPLICATION>/<String>
    동일한 suffix가 존재하지 않도록 해야 한다.
    브라우저 접근시 "http://JUPYTERHUB_HOST:PORT/<APPLICATION>/<String>/"
    traefix 사용시 JUPYTERHUB_HOST:PORT 없이 jupyter 도메인으로 접근 가능하다.
-h, --help
    도움말

Example
-------
    chp-cli create voila -s moon -p 8866 moon.ipynb
    chp-cli remove voila -s moon
    chp-cli status voila
    chp-cli create tensorboard -s board -p 6000 logdir
    chp-cli remove tensorboard -s board
    chp-cli status tensorboard
    ''')

def main():
    proxy = None
    proxy_url = None
    argument = None
    port = None
    suffix = None
    help = False
    action = 'status'
    application = None

    try:
        if len(sys.argv) > 2 and sys.argv[1] and sys.argv[2]:
            action = sys.argv[1]
            application = sys.argv[2]
            if action in ('-h', '--help'):
                help = True
            elif action not in ('create', 'remove', 'status'):
                raise getopt.GetoptError('ACTION: ' + action)
        else:
            raise getopt.GetoptError('OPTIONS')
            
 
        opts, args = getopt.getopt(sys.argv[3:], 'p:s:h', ['port=', 'suffix=', 'help'])
        for o, a in opts:
            if o in ('-p', '--port'):
                port = a
            elif o in ('-s', '--suffix'):
                suffix = a
            elif o in ('-h', '--help'):
                help = True
            else:
                assert 'Unhandled options'

        if help:
            usage()
            sys.exit(0)
            
        proxy = Proxy(application)
        method = getattr(proxy, action)
        
        def handler(signum, frame):
            proxy.remove(suffix)

        signals = (signal.SIGINT, signal.SIGTERM)
        for sig in signals:
            signal.signal(
                sig,
                handler
            )

        if action == 'create':
            if port is None or suffix is None:
                raise getopt.GetoptError('port or suffix is None')
            hostname = socket.gethostname()
            proxy_url = 'http://' + hostname + ':' + port

            if os.path.exists(args[0]):
                argument = args[0]
            else:
                raise getopt.GetoptError('{} file is not exist'.format(args[0]))
            method(suffix, proxy_url)
            ret = json.dumps(proxy.status())
            if ret != '{}':
                print(ret)
            t = Thread(target=globals()[application], args=(suffix, port, argument))
            t.start()
            t.join()
        elif action == 'remove':
            if suffix is None:
                raise getopt.GetoptError('suffix is None')
            pslist = getoutput("ps -elf | grep chp-cli | grep '\(--suffix\|-s\)\([= ]\)\?{} ' | grep -v grep | grep -v remove".format(suffix)).split('\n')
            if len(pslist) > 0 and pslist[0] != '':
                for ps in pslist:
                    item = ps.split()
                    pgid = item[3]
                    os.killpg(int(pgid), signal.SIGTERM)
                    print('Stop: ' + ' '.join(item[14:]))
            method(suffix)
        else:
            method()
            ret = json.dumps(proxy.status())
            if ret != '{}':
                print(ret)
            
    except Exception as e:
        if proxy:
            proxy.remove(suffix)
        raise e
    
    sys.exit(0)
