from decouple import config
import jwt, datetime
from app_shopping.models import *

def adminGenerateToken(fetchuser):
    try:
        secret_key = config("Admin_jwt_token")
        total_days = 1
        token_payload = {
            "id": str(fetchuser.id),
            "email":fetchuser.email,
            "iat": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days= total_days),  
        }
        detail_payload = {
            "id": str(fetchuser.id),
            "email":fetchuser.email,
            "first_name": fetchuser.first_name,
            "last_name": fetchuser.last_name,
            "phone": fetchuser.phone,
            "image": fetchuser.image.url
        }
        token = jwt.encode(token_payload, key= secret_key, algorithm="HS256")
        AdminWhitelistToken.objects.create(admin = fetchuser, token = token)
        return {"status": True, "token" : token, "payload": detail_payload}
    except Exception as e:
        return {"status": False, "message": f"Error during generationg token {str(e)}"}
    