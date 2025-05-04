from os import environ
from dotenv import load_dotenv

load_dotenv()


class Var(object):
    MULTI_CLIENT = False
    API_ID = int(environ.get("API_ID","7326452"))
    API_HASH = str(environ.get("API_HASH","a865401e13d06664d7ffa3558f8e2940"))
    SESSION_NAME = str(environ.get('SESSION_NAME', 'AvishkarPatil'))
    BOT_TOKEN = str(environ.get("BOT_TOKEN","1940498592:AAENjs-8x0m_nXmapmMIjMjXHK0aaC0kuTI" ))
    BROADCAST_AS_COPY = bool(environ.get("BROADCAST_AS_COPY", False))
    SLEEP_THRESHOLD = int(environ.get("SLEEP_THRESHOLD", "60"))  # 1 minte
    WORKERS = int(environ.get("WORKERS", "6"))  # 6 workers = 6 commands at once
    BIN_CHANNEL = int(
        environ.get("BIN_CHANNEL", "-1001536023432")
    )  # you NEED to use a CHANNEL when you're using MULTI_CLIENT
    PORT = int(environ.get("PORT", 8080))
    BIND_ADDRESS = str(environ.get("WEB_SERVER_BIND_ADDRESS", "0.0.0.0"))
    PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))  # 20 minutes
    HAS_SSL = environ.get("HAS_SSL", False)
    HAS_SSL = True if str(HAS_SSL).lower() == "true" else False
    OWNER_ID = int(environ.get('OWNER_ID' , "1913411555"))
    NO_PORT = environ.get("NO_PORT", False)
    NO_PORT = True if str(NO_PORT).lower() == "true" else False
    if "DYNO" in environ:
        ON_HEROKU = True
        APP_NAME = str(environ.get("APP_NAME", "SpeedXstreamz"))
    else:
        ON_HEROKU = False
    DATABASE_URL = str(environ.get('DATABASE_URL'))
    UPDATES_CHANNEL = environ.get("UPDATES_CHANNEL", None)
    FORCE_SUB_ENABLED = environ.get("FORCE_SUB_ENABLED", "True").lower() == "true"
    BANNED_CHANNELS = list(set(int(x) for x in str(environ.get("BANNED_CHANNELS", "-100")).split()))

    # CRITICAL FIX: Handle the new Heroku URL format with random strings (APPNAME-IDENTIFIER.herokuapp.com)
    # The FQDN must be set correctly for file links to work

    # Option 1: Use HEROKU_DOMAIN if explicitly set (highest priority)
    if environ.get("HEROKU_DOMAIN"):
        FQDN = str(environ.get("HEROKU_DOMAIN"))
        print(f"Using HEROKU_DOMAIN: {FQDN}")

    # Option 2: Use FQDN if explicitly set (second priority)
    elif environ.get("FQDN"):
        FQDN = str(environ.get("FQDN"))
        print(f"Using FQDN: {FQDN}")

    # Option 3: Extract domain from HEROKU_APP_URL if available (third priority)
    elif ON_HEROKU and environ.get("HEROKU_APP_URL"):
        heroku_url = str(environ.get("HEROKU_APP_URL"))
        # Clean up the URL
        heroku_url = heroku_url.replace("https://", "").replace("http://", "").rstrip("/")
        # If it contains herokuapp.com, use it as is
        if ".herokuapp.com" in heroku_url:
            FQDN = heroku_url
        else:
            # Otherwise append herokuapp.com
            FQDN = f"{heroku_url}.herokuapp.com"
        print(f"Using domain from HEROKU_APP_URL: {FQDN}")

    # Option 4: Use APP_NAME with .herokuapp.com (fallback, may not work with newer apps)
    elif ON_HEROKU:
        FQDN = APP_NAME + ".herokuapp.com"
        print(f"WARNING: No domain configuration found. Using {FQDN} which may not work with newer Heroku apps.")
        print("Please set the HEROKU_DOMAIN environment variable to your exact Heroku domain.")
        print("Example: your-app-name-1234567890ab.herokuapp.com (without https:// or trailing slash)")

    # Option 5: Not on Heroku, use BIND_ADDRESS
    else:
        FQDN = BIND_ADDRESS

    if ON_HEROKU:
        URL = f"https://{FQDN}/"
    else:
        URL = "http{}://{}{}/".format(
            "s" if HAS_SSL else "", FQDN, "" if NO_PORT else ":" + str(PORT)
        )
