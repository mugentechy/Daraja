from flask import request, jsonify, render_template, Blueprint
import base64, time, os, requests

blueprint = Blueprint('app', __name__)

# Environment Variables (Set in .env or system variables)
CONSUMER_KEY = os.getenv('CONSUMER_KEY') 
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')  
BUSINESS_SHORTCODE = os.getenv('BUSINESS_SHORTCODE')
PASSKEY = os.getenv('PASSKEY') 
CALLBACK_URL = os.getenv('CALLBACK_URL') 
QR_CODE_URL = "https://sandbox.safaricom.co.ke/mpesa/qrcode/v1/generate"

# Function to Get Access Token
def get_access_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    try:
        response = requests.get(url, auth=(CONSUMER_KEY, CONSUMER_SECRET))
        response.raise_for_status()
        data = response.json()
        return data.get("access_token")
    except requests.exceptions.RequestException as e:
        print("Error fetching access token:", e)
        return None

# Function to initiate STK push
def initiate_stk_push(phone, amount):
    timestamp = time.strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(f"{BUSINESS_SHORTCODE}{PASSKEY}{timestamp}".encode()).decode()
    
    payload = {
        "BusinessShortCode": BUSINESS_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": BUSINESS_SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": CALLBACK_URL,
        "AccountReference": "2255",
        "TransactionDesc": "Test Payment"
    }
    
    headers = {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/json"
    }
    
    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# Routes
@blueprint.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@blueprint.route("/pay", methods=["POST"])
def pay():
    phone = request.form.get("phone")
    amount = request.form.get("amount")
    response = initiate_stk_push(phone, amount)
    return jsonify(response)

@blueprint.route("/callback", methods=["POST"])
def callback():
    response = request.get_json()
    with open("M_PESAConfirmationResponse.txt", "a") as log:
        log.write(str(response) + "\n")
    return jsonify({"ResultCode": 0, "ResultDesc": "Confirmation Received Successfully"})

@blueprint.route("/qr", methods=["GET"])
def qr_page():
    return render_template("qr.html")

# Function to Generate QR Code
def generate_qr_code(amount):
    access_token = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "MerchantName": "TEST SUPERMARKET",
        "RefNo": "Invoice Test",
        "Amount": amount,
        "TrxCode": "BG",
        "CPI": "373132",
        "Size": "300"
    }
    response = requests.post(QR_CODE_URL, json=payload, headers=headers)
    return response.json()

# QR Code API Endpoint
@blueprint.route('/generate_qr', methods=['POST'])
def generate_qr():
    amount = request.form.get("amount")
    qr_response = generate_qr_code(amount)
    return jsonify(qr_response)
