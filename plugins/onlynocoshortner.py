import base64 
from config import ON_SHORT_URL

def onlynoco_shortner(url):
    onshort = base64.urlsafe_b64encode(url.encode()).decode().rstrip("=") 
    short_url = f"{ON_SHORT_URL}/redirect?code={onshort}"

    return short_url