import os

from dotenv import load_dotenv

load_dotenv()

THERMIA_HOST = os.environ.get("THERMIA_HOST", "172.16.2.178")
THERMIA_PORT = int(os.environ.get("THERMIA_PORT", "502"))
THERMIA_UNIT_ID = int(os.environ.get("THERMIA_UNIT_ID", "1"))

HOUSE_API_URL = os.environ.get(
    "HOUSE_API_URL", "http://malina.mm/house/cgi-bin/house.py"
)

BUS_STOP_SITE_ID = int(os.environ.get("BUS_STOP_SITE_ID", "2216"))
TRAIN_STOP_SITE_ID = int(os.environ.get("TRAIN_STOP_SITE_ID", "9633"))
BUS_STOP_WALK_MINUTES = int(os.environ.get("BUS_STOP_WALK_MINUTES", "6"))
TRAIN_STOP_WALK_MINUTES = int(os.environ.get("TRAIN_STOP_WALK_MINUTES", "10"))
