from flask import Flask, request, jsonify, make_response
import requests
import binascii
import jwt
import urllib3
import json
import warnings
import re
import time
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

try:
    import my_pb2
    import output_pb2
except ImportError:
    pass

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

xK9mP = b'Yg&tc%DEuh6%Zc^8'
nH4qR = b'6oyZDr22E3ychjM%'

cV6xW = "OB54"
dF9qZ = "https://100067.connect.garena.com/oauth/guest/token/grant"

def iJ7kL(data_bytes):
    cipher = AES.new(xK9mP, AES.MODE_CBC, nH4qR)
    padded = pad(data_bytes, AES.block_size)
    return cipher.encrypt(padded)

def mN8oP(response_content):
    try:
        example_msg = output_pb2.Garena_420()
        example_msg.ParseFromString(response_content)
        response_dict = {}
        lines = str(example_msg).split("\n")
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                response_dict[key.strip()] = value.strip().strip('"')
        return response_dict
    except Exception as e:
        return {"error": str(e)}

def qR9sT(uid, password):
    payload = {
        'uid': str(uid),
        'password': str(password),
        'response_type': "token",
        'client_type': "2",
        'client_secret': "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        'client_id': "100067"
    }
    headers = {
        'User-Agent': "GarenaMSDK/4.0.19P9(SM-M526B ;Android 13;pt;BR;)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'ReleaseVersion': cV6xW
    }
    try:
        resp = requests.post(dF9qZ, data=payload, headers=headers, verify=False, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            if 'access_token' in data and 'open_id' in data:
                return data.get('access_token'), data.get('open_id')
    except Exception as e:
        print(f"Guest login error: {e}")
    return None, None

def uV1wX(access_token, open_id):
    url = "https://loginbp.ggpolarbear.com/MajorLogin"
    
    game_data = my_pb2.GameData()
    game_data.timestamp = "2024-12-05 18:15:32"
    game_data.game_name = "free fire"
    game_data.game_version = 1
    game_data.version_code = "1.126.1"
    game_data.os_info = "Android OS 9 / API-28 (PI/rel.cjw.20220518.114133)"
    game_data.device_type = "Handheld"
    game_data.network_provider = "Verizon Wireless"
    game_data.connection_type = "WIFI"
    game_data.screen_width = 1280
    game_data.screen_height = 960
    game_data.dpi = "240"
    game_data.cpu_info = "ARMv7 VFPv3 NEON VMH | 2400 | 4"
    game_data.total_ram = 5951
    game_data.gpu_name = "Adreno (TM) 640"
    game_data.gpu_version = "OpenGL ES 3.0"
    game_data.user_id = "Google|74b585a9-0268-4ad3-8f36-ef41d2e53610"
    game_data.ip_address = "172.190.111.97"
    game_data.language = "en"
    game_data.open_id = open_id
    game_data.access_token = access_token
    game_data.platform_type = 4
    game_data.field_99 = "4"
    game_data.field_100 = "4"
    
    try:
        serialized_data = game_data.SerializeToString()
    except Exception as e:
        return {"error": f"Protobuf serialization failed: {str(e)}"}
    
    encrypted_data = iJ7kL(serialized_data)

    headers = {
        'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/octet-stream",
        'Expect': "100-continue",
        'X-GA': "v1 1",
        'X-Unity-Version': "2018.4.11f1",
        'ReleaseVersion': cV6xW
    }

    try:
        response = requests.post(url, data=encrypted_data, headers=headers, verify=False, timeout=15)
        
        if response.status_code == 200:
            parsed = mN8oP(response.content)
            jwt_token = parsed.get("token", "")
            if jwt_token and jwt_token not in ["", "N/A", "null"]:
                return {
                    "token": jwt_token,
                    "region": parsed.get("region", "N/A"),
                    "status": "success"
                }
            else:
                return {"error": "No valid token in response", "raw": parsed}
        else:
            return {"error": f"HTTP {response.status_code}", "raw": response.text}
    except Exception as e:
        return {"error": str(e)}

def yZ2aB(nickname):
    if len(nickname) < 4 or len(nickname) > 14:
        return False, "Length must be 4-14 characters"
    if not re.match(r'^[a-zA-Z0-9_]+$', nickname):
        return False, "Only letters, numbers and underscore allowed"
    if nickname[0].isdigit():
        return False, "Cannot start with a number"
    return True, "Valid"

def cD4eF(nickname):
    nickname_bytes = nickname.encode('utf-8')
    ts = int(time.time())
    payload = bytearray()
    
    payload.append(0x0A)
    payload.append(len(nickname_bytes))
    payload.extend(nickname_bytes)
    
    payload.append(0x10)
    while ts > 127:
        payload.append((ts & 0x7F) | 0x80)
        ts >>= 7
    payload.append(ts)
    
    return bytes(payload)

def gH5iJ(token, nickname):
    url = "https://loginbp.ggpolarbear.com/MajorModifyNickname"
    payload_bytes = cD4eF(nickname)
    encrypted_data = iJ7kL(payload_bytes)
    
    headers = {
        'Authorization': f'Bearer {token}',
        'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/octet-stream",
        'X-GA': "v1 1",
        'X-Unity-Version': "2018.4.11f1",
        'ReleaseVersion': cV6xW
    }
    
    try:
        response = requests.post(url, data=encrypted_data, headers=headers, verify=False, timeout=10)
        return {'status': response.status_code, 'response': response.text}
    except Exception as e:
        return {'status': 500, 'response': str(e)}

def kL6mN(token):
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        uid = decoded.get("account_id")
        name = decoded.get("nickname")
        region = decoded.get("lock_region") or decoded.get("region") or decoded.get("noti_region")
        country = decoded.get("country_code")
        return {
            "uid": str(uid) if uid else None,
            "name": name,
            "region": region.upper() if region else None,
            "country": country,
            "raw": decoded
        }
    except Exception as e:
        print(f"JWT decode error: {e}")
        return None

@app.route('/Bmw', methods=['GET'])
def bmw_endpoint():
    # Get all parameters
    uid = request.args.get('uid')
    password = request.args.get('password')
    access_token = request.args.get('access')
    jwt_token_param = request.args.get('jwt')
    nickname = request.args.get('nickname')
    
    # Validate nickname first (required for all methods)
    if not nickname:
        response_text = """CrEdIt => @narutocodexff
JoIn => @narutocodexofc
StAtUs => ❌ Missing nickname parameter
CoDe => 400"""
        response = make_response(response_text)
        response.headers["Content-Type"] = "text/plain"
        return response, 400
    
    is_valid, validation_msg = yZ2aB(nickname)
    if not is_valid:
        response_text = f"""CrEdIt => @narutocodexff
JoIn => @narutocodexofc
StAtUs => ❌ {validation_msg}
CoDe => 400"""
        response = make_response(response_text)
        response.headers["Content-Type"] = "text/plain"
        return response, 400
    
    # Determine which method to use
    if jwt_token_param:
        # Method 3: Using JWT token directly
        jwt_token = jwt_token_param
        
    elif access_token and not uid:
        # Method 2: Using access token and open_id (need open_id)
        open_id = request.args.get('open_id')
        if not open_id:
            response_text = """CrEdIt => @narutocodexff
JoIn => @narutocodexofc
StAtUs => ❌ Missing open_id parameter
CoDe => 400"""
            response = make_response(response_text)
            response.headers["Content-Type"] = "text/plain"
            return response, 400
        
        login_result = uV1wX(access_token, open_id)
        if "error" in login_result:
            response_text = f"""CrEdIt => @narutocodexff
JoIn => @narutocodexofc
StAtUs => ❌ MajorLogin failed
DeTaIlS => {login_result.get('error')}
CoDe => 401"""
            response = make_response(response_text)
            response.headers["Content-Type"] = "text/plain"
            return response, 401
        
        jwt_token = login_result.get("token")
        if not jwt_token or jwt_token == "N/A":
            response_text = """CrEdIt => @narutocodexff
JoIn => @narutocodexofc
StAtUs => ❌ No JWT token
CoDe => 401"""
            response = make_response(response_text)
            response.headers["Content-Type"] = "text/plain"
            return response, 401
        
        region = login_result.get('region', 'N/A')
        
    elif uid and password:
        # Method 1: Using UID and password
        acc_token, open_id = qR9sT(uid, password)
        
        if not acc_token or not open_id:
            response_text = """CrEdIt => @narutocodexff
JoIn => @narutocodexofc
StAtUs => ❌ Guest Login Failed
CoDe => 401"""
            response = make_response(response_text)
            response.headers["Content-Type"] = "text/plain"
            return response, 401
        
        login_result = uV1wX(acc_token, open_id)
        if "error" in login_result:
            response_text = f"""CrEdIt => @narutocodexff
JoIn => @narutocodexofc
StAtUs => ❌ MajorLogin failed
DeTaIlS => {login_result.get('error')}
CoDe => 401"""
            response = make_response(response_text)
            response.headers["Content-Type"] = "text/plain"
            return response, 401
        
        jwt_token = login_result.get("token")
        if not jwt_token or jwt_token == "N/A":
            response_text = """CrEdIt => @narutocodexff
JoIn => @narutocodexofc
StAtUs => ❌ No JWT token in login response
CoDe => 401"""
            response = make_response(response_text)
            response.headers["Content-Type"] = "text/plain"
            return response, 401
        
        region = login_result.get('region', 'N/A')
        
    else:
        response_text = """CrEdIt => @narutocodexff
JoIn => @narutocodexofc
StAtUs => ❌ Invalid parameters
CoDe => 400
MeThOdS:
  1. /Bmw?uid=UID&password=PASSWORD&nickname=NICKNAME
  2. /Bmw?access=ACCESS_TOKEN&open_id=OPEN_ID&nickname=NICKNAME
  3. /Bmw?jwt=JWT_TOKEN&nickname=NICKNAME"""
        response = make_response(response_text)
        response.headers["Content-Type"] = "text/plain"
        return response, 400
    
    # Change nickname using JWT token
    result = gH5iJ(jwt_token, nickname)
    jwt_info = kL6mN(jwt_token)
    
    # Format response
    response_text = f"""CrEdIt => @narutocodexff
JoIn => @narutocodexofc
NiCkNaMe => {nickname}
UiD => {jwt_info.get('uid') if jwt_info else uid or 'N/A'}
ReGiOn => {region if 'region' in locals() else jwt_info.get('region', 'N/A')}
JwT_ToKeN => {jwt_token}
NaMe => {jwt_info.get('name') if jwt_info else 'N/A'}
StAtUs => {'Success ✅' if result['status'] == 200 else '❌ Failed'}
HtTp_CoDe => {result['status']}
SeRvEr_ReSpOnSe => {result['response']}"""

    response = make_response(response_text)
    response.headers["Content-Type"] = "text/plain"
    return response

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)