import os
import sys
import h5py
import json
import hmac
import time
import base64 
import hashlib
import logging
import requests

import numpy as np

from pathlib import Path
from requests.auth import AuthBase
from datetime import datetime as dt
from base64 import b64encode as b64e
from twisted.internet import task, reactor

API_PASS = os.environ["API_PASS"]
API_SECRET = os.environ["API_SECRET"]
API_KEY = os.environ["API_KEY"]

# Create custom authentication for Exchange
class CoinbaseExchangeAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or "")
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message.encode(), hashlib.sha256)
        signature_b64 = b64e(signature.digest()).rstrip(b"\n")

        request.headers.update(
            {
                "CB-ACCESS-SIGN": signature_b64,
                "CB-ACCESS-TIMESTAMP": timestamp,
                "CB-ACCESS-KEY": self.api_key,
                "CB-ACCESS-PASSPHRASE": self.passphrase,
                "Content-Type": "application/json",
            }
        )
        return request

def get_curr_price_points(api_url, currency):
    #resp = requests.get(api_url + ("/v2/prices/%s-USD/buy" % currency))
    resp = send_req(api_url + ("/v2/prices/%s-USD/buy" % currency))
    buy = resp.json()["data"]["amount"]

    #resp = requests.get(api_url + ("/v2/prices/%s-USD/sell" % currency))
    resp = send_req(api_url + ("/v2/prices/%s-USD/sell" % currency))
    sell = resp.json()["data"]["amount"]

    #resp = requests.get(api_url + ("/v2/prices/%s-USD/spot" % currency))
    resp = send_req(api_url + ("/v2/prices/%s-USD/spot" % currency))
    spot = resp.json()["data"]["amount"]

    return buy, sell, spot


def query_coinbase():
    api_url = "https://api.coinbase.com"
    pro_api_url = "https://api.pro.coinbase.com"
    auth = CoinbaseExchangeAuth(API_KEY, API_SECRET, API_PASS)

    #resp = requests.get(pro_api_url + "/products/BTC-USD/book?level=3", auth=auth).json()
    resp = send_req(pro_api_url + "/products/BTC-USD/book?level=3", auth).json()

    dtype = np.dtype([("price", np.float32, 1), ("size", np.float32, 1)])
    bids = np.asarray(
        [(price, size) for price, size, order_id in resp["bids"]], dtype=dtype
    )
    asks = np.asarray(
        [(price, size) for price, size, order_id in resp["asks"]], dtype=dtype
    )

    fname = "/data/%s.hdf" % dt.utcnow().strftime("%d-%m-%y")
    if not Path(fname).exists():
        Path(fname).touch()

    with h5py.File(fname, "r+") as f:
        ts = dt.utcnow().strftime("%H%M:%S")
        grp = f.create_group(ts)
        price_pnt_grp = grp.create_group("price-points")

        bids_dset = grp.create_dataset("bids", data=bids, compression="gzip")
        asks_dset = grp.create_dataset("asks", data=asks, compression="gzip")

        dtype = np.dtype([("buy", np.float32, 1), ("sell", np.float32, 1), ("spot", np.float32, 1)])
        currency_list = ["BTC", "ETH", "XRP", "LTC"]
        for curr in currency_list:
            resp = get_curr_price_points(api_url, curr)
            ndarr = np.asarray(resp, dtype=dtype)

            # setting gzip compression breaks things
            price_pnt_grp.create_dataset(curr, data=ndarr)

            # defensive rate limiting to prevent exceeding coinbase limits
            time.sleep(1)

    logging.warning("Data written to: %s" % fname)
    sys.stdout.flush()


def send_req(url, auth=None):
    retry = True
    while retry:
        try:
            if auth:
                resp = requests.get(url, auth=auth)
            else:
                resp = requests.get(url)

            retry = False
            return resp
        except Exception as ex:
            logging.error(ex)
            time.sleep(0.5)

# ref to finish: https://stackoverflow.com/a/30610511
def merge_hdf(master, filenames):
    master_hdf = h5py.File(master, "w")
    for fname in filenames:
        source_hdf = h5py.File(fname, "r")
        for k, v in source_hdf.items():
            pass
            # master_hdf.create_dataset()


if __name__ == "__main__":
    l = task.LoopingCall(query_coinbase)
    l.start(60.0)
    reactor.run()

