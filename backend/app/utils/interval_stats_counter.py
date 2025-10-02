import base64
import datetime

from config.database import get_db_connection
import os

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from dotenv import load_dotenv
import json

from pymongo.database import Database

load_dotenv()

class IntervalStatsCounter:
    def __init__(self, module: str):
        self.module = module
    def count(self, act: str, type: str = None, val: float = 1, modular: str = "hour"):
        with get_db_connection() as client:
            db: Database = client['comp5241_g10']
            curr_time = datetime.datetime.now(datetime.timezone.utc)
            rounded = curr_time.timestamp()
            if modular == "day":
                rounded = int(rounded//86400) * 86400
            else:
                rounded = int(rounded//3600) * 3600
            if type is None:
                db["interval_stats"].find_one_and_update({"module": self.module, "act": act, "interval_num": rounded},
                                                         {"$inc":{"val": val}}, upsert=True)
            else:
                db["interval_stats"].find_one_and_update({"module": self.module, "act": act, "type": type, "interval_num": rounded},
                                                         {"$inc":{"val": val}}, upsert=True)