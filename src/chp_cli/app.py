def voila(suffix, port, ipynb, theme='dark', template='lab'):
    cmd = ['voila',
        '--no-browser',
        '--theme=' + theme,
        '--port=' + str(port),
        '--enable_nbextensions=False',
        '--server_url=/voila/' + suffix,
        '--base_url=/voila/' + suffix + '/',
        '--Voila.ip=0.0.0.0',
        ipynb 
    ] 
    run(cmd)
    

def tensorboard(suffix, port, logdir):
    cmd = ['tensorboard',
        '--port', + str(port),
        '--logdir=', + logdir
    ]
    run(cmd)
