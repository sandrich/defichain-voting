import requests
import json

req = requests.get('https://api.github.com/repos/DeFiCh/dfips/issues?state=open')
data = req.json()

ownerAddresses = ['ADD_HERE']
defiConf = '/Users/USER_NAME/Library/Application Support/Defi/.defi/defi.conf'

def _readConfig(defi_conf):
        conf = {}
        with open(defi_conf) as f:
            lines = f.read().splitlines()
            ignore = False

            for line in lines:
                var = line.split('=', 1)

                if len(var) == 1 and 'test' in var[0]:
                    ignore = True
                elif len(var) == 1 and 'main' in var[0]:
                    ignore = False

                if var[0] in ['rpcuser', 'rpcpassword', 'rpcport'] and not ignore:
                    conf[var[0]] = var[1]

        return conf

def _rpcquery(conf, method, params=False):
    '''
        Wrapper to run DefiChain RPC commands
    '''
    if not params:
        params = []
    elif not isinstance(params, list):
        params = [params]

    headers = {'Content-type': 'application/json'}
    data = {
        'jsonrpc': '1.0',
        'id': 'curltest',
        'method': method,
        'params': params
    }

    rpchost = f'http://localhost:{conf["rpcport"]}'
    rpcuser = conf['rpcuser']
    rpcpassword = conf['rpcpassword']

    try:
        response = requests.post(rpchost, auth=(rpcuser, rpcpassword), headers=headers, data=json.dumps(data), timeout=1000)
        response.raise_for_status()

        data = response.json()

        if 'result' in data:
            return data['result']
        return data
    except requests.exceptions.ConnectionError:
        raise SystemExit()

def main():

    conf = _readConfig(defiConf)
    responses = []

    for d in data:
        labels = list(map(lambda l: l['name'], d['labels']))
        
        if 'round/2208' in labels and 'announcement' not in labels:
            s = d['title'].split(':')
            id = s[0]
            title = s[1]

            answer = input(f'{d["title"]} [yes/no]: ')
            if answer not in ['yes', 'no']:
                exit('Not a valid answer. Only yes / no valid')
            

            signatures = ''
            for owner in ownerAddresses:
                cfpAnswer = f'{id}-{answer}'.lower()
                sign = _rpcquery(conf, 'signmessage', [owner, cfpAnswer])
                signatures += f'\nsignmessage {owner} {cfpAnswer}\n{sign}'

            responses.append({
                'url': d["html_url"],
                'title': f'{id}: {title}\n{d["html_url"]}',
                'signatures': signatures
            })

    for response in responses:
        print('\n------------------------------------------------------')
        print(f'{response["title"]}')
        print('------------------------------------------------------\n')
        print(f'{response["signatures"]}')



if __name__ == "__main__":
    main()

