from datetime import date
from datetime import datetime
import base64
import json
import hmac
import hashlib
import string
import random



def calculate_age(born):
    if born == None:
        return date.today()
    else:
        today = date.today()
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def validate_one_character(string):

    if len(string) > 1:
        return False
    else:
        if string == "1"  or string == "0":
            return True
        else:
            return False


# App key + secret
APPLICATION_KEY = 'fe851d0c-f991-4ad7-8607-7bdd1695ae5d'
APPLICATION_SECRET = 'F9ckfxFEn0+2jtsq9/dDNA=='


def getAuthTicket(user):
    userTicket = {
        'identity': {'type': 'username', 'endpoint': user['username']},
        'expiresIn': 3600, #1 hour expiration time of session when created using this ticket
        'applicationKey': APPLICATION_KEY,
        'created': datetime.utcnow().isoformat()
    }

    try:
        userTicketJson = json.dumps(userTicket).replace(" ", "")
        userTicketBase64 = base64.b64encode(userTicketJson.encode('ascii'))


        # TicketSignature = Base64 ( HMAC-SHA256 ( ApplicationSecret, UTF8 ( UserTicketJson ) ) )
        digest = hmac.new(base64.b64decode(APPLICATION_SECRET), msg=userTicketJson.encode('ascii'), digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(digest)

        print(type(userTicketBase64))
        print(type(signature))
        two_points = b':'
        print(type(two_points))
        # UserTicket = TicketData + ":" + TicketSignature
        #signedUserTicket = userTicketBase64 + ':' + signature
        signedUserTicket = userTicketBase64 + two_points + signature

        #return {'userTicket': signedUserTicket}
        return signedUserTicket
    except Exception as inst:
        print(inst)



def code_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))