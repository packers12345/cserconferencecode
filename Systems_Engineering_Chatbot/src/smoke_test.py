import urllib.request
import urllib.parse
import json

BASE = 'http://127.0.0.1:5001'

def get_root():
    with urllib.request.urlopen(BASE + '/') as r:
        return r.read().decode('utf-8')

def post_form(path, data):
    data_enc = urllib.parse.urlencode(data).encode('utf-8')
    req = urllib.request.Request(BASE + path, data=data_enc, method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    with urllib.request.urlopen(req) as r:
        return r.read().decode('utf-8')

if __name__ == '__main__':
    print('GET /')
    try:
        print(get_root())
    except Exception as e:
        print('GET / error:', e)

    print('\nPOST /chat')
    try:
        print(post_form('/chat', {'prompt': 'Create system requirements for a GPS satellite'}))
    except Exception as e:
        print('POST /chat error:', e)

    print('\nPOST /l1_mapping')
    try:
        print(post_form('/l1_mapping', {'prompt': 'create an L1 mapping for a mechanical spring and an electric circuit model'}))
    except Exception as e:
        print('POST /l1_mapping error:', e)

    print('\nPOST /morphism_proof')
    try:
        print(post_form('/morphism_proof', {'prompt': 'create a morphism for a mechanical spring and an electric circuit'}))
    except Exception as e:
        print('POST /morphism_proof error:', e)
