import requests
import hashlib
import base64
import random
import string
import urllib.parse
import phpserialize

from .models import DataCenter


class VirtualizorAdminAPI:
    def __init__(self, ip, key, passw, port=4084):
        self.key = key
        self.passw = passw
        self.ip = ip
        self.port = port
        self.protocol = 'http'
    
    def make_apikey(self, key, passw):
        return key + hashlib.md5((passw + key).encode('utf-8')).hexdigest()

    def generateRandStr(self, length):
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length)).lower()
    
    def call(self, path, data=None, post=None, cookies=None):
        try:
            key = self.generateRandStr(8)
            apikey = self.make_apikey(key, self.passw)

            url = f'{self.protocol}://{self.ip}:{self.port}/{path}'
            url += f'&adminapikey={urllib.parse.quote(self.key)}&adminapipass={urllib.parse.quote(self.passw)}'
            url += f'&api=serialize&apikey={urllib.parse.quote(apikey)}'

            if data:
                url += f'&apidata={urllib.parse.quote(base64.b64encode(data.encode("utf-8")).decode("utf-8"))}'

            headers = {
                'User-Agent': 'Softaculous'
            }

            if cookies:
                cookies = {k: v for k, v in cookies.items()}

            if post:
                response = requests.post(url, headers=headers, data=post, cookies=cookies, verify=False)
            else:
                response = requests.get(url, headers=headers, cookies=cookies, verify=False)

            response.raise_for_status()
            return phpserialize.loads(response.text.encode('utf-8'))

        except requests.exceptions.RequestException as e:
            print(f"HTTP Request failed: {e}")
            return None

    def manage_vps(self, post):
        path = f'index.php?act=managevps&vpsid={post["vpsid"]}'
        result = self.call(path, post=post)

        if result:
            try:
                return {
                    'title': result.get(b'title').decode('utf-8'),
                    'done': result.get(b'done', False),
                    'error': [err.decode('utf-8') for err in result.get(b'error', [])],
                    'vs_info': result.get(b'vps'),
                    'vps_data': result.get(b'vps_data')
                }
            except Exception as e:
                print(f"Deserialization failed: {e}")
                return None
        else:
            return None

    def update_bandwidth(self, vpsid, bandwidth):
        post_data = {
            "vpsid": str(vpsid),
            "bandwidth": str(bandwidth),
            "theme_edit": 1,
            "editvps": 1
        }

        result = self.manage_vps(post_data)

        if result:
            if result.get('error'):
                print(f"Failed to update bandwidth: {result['error']}")
            else:
                print(f"Bandwidth updated successfully for VPS ID {vpsid}.")
            return result
        else:
            print("Failed to update VPS bandwidth due to an API error.")
            return None


def update_vps_bandwidth(data_center_id, vpsid, bandwidth):
    try:
        dc = DataCenter.objects.get(id=data_center_id)
        api = VirtualizorAdminAPI(dc.ip_address, dc.api_key, dc.api_password, dc.port)
        result = api.update_bandwidth(vpsid, bandwidth)
        return result
    except DataCenter.DoesNotExist:
        print("Data center not found")
        return {"error": "Data center not found"}