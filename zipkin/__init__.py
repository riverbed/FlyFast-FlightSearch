# /**********************************/
# /*       Copyright (c) 2021       */
# /*         Aternity, Inc.         */
# /*      All Rights Reserved.      */
# /**********************************/

import codecs
import json
import logging
import os
import socket

import requests
from py_zipkin.zipkin import zipkin_span
from py_zipkin.request_helpers import create_http_headers
from py_zipkin.transport import BaseTransportHandler


LOGGER = logging.getLogger("aternity.zipkin")


class Json2Transport(BaseTransportHandler):
    def __init__(self):
        super(Json2Transport, self).__init__()
        self.enabled = False

        self.url = os.environ.get("COLLECTOR_URL")

        if self.url is None:
            self.get_collector_url_from_config_file()
            if self.enabled and self.url is None:
                LOGGER.error("Enabled but not valid URL")
                self.enabled = False
            else:
                LOGGER.info("Using zipkin configuration: Instrument: %s, Url: %s", self.enabled, self.url)
        else:
            LOGGER.info("Using COLLECTOR_URL environment variable, ENABLED is true by default")
            self.enabled = True

    def get_collector_url_from_config_file(self):
        config = {}
        try:
            with codecs.open("/opt/appinternals/config/zipkin_config.json", "r", encoding="utf-8") as infile:
                config = json.load(infile)
        except IOError:
            LOGGER.debug("No zipkin config file. Not instrumenting")
        except ValueError:
            LOGGER.error("Could not parse zipkin config, will not send spans")

        self.url = config.get("url")
        self.enabled = config.get("instrument", False)
        self.ip = config.get("ip")

    def get_max_payload_bytes(self):
        return None

    def send(self, encoded_span):
        if self.enabled:
            try:
                response = requests.post(
                    self.url,
                    data=encoded_span,
                    headers={'Content-Type': 'application/json'},
                )

                response.raise_for_status()
            except requests.exceptions.ConnectTimeout:
                LOGGER.error("Could not connect to Zipkin at %s", self.url)
            except IOError:
                LOGGER.exception("Could not send span to Zipkin")


TRANSPORT = None
def get_transport():
    global TRANSPORT
    if TRANSPORT is None:
        TRANSPORT = Json2Transport()

    return TRANSPORT

def get_zipkin_url():
    transport = get_transport()
    return transport.url
