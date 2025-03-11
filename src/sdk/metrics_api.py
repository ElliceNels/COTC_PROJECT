from time import sleep
import json
import logging
import requests
from config import config
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os
import subprocess

logger = logging.getLogger(__name__)

class MetricsAPI:
    failed_data = []

    @staticmethod
    def send_metrics(data: list):
        # API to send metrics data to the web app
        url = config.server.url + '/store_metrics'
        headers = {'Content-Type': 'application/json'}
        
        # Setup retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],  # Status codes that trigger a retry
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]  # HTTP methods to retry
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        http = requests.Session()
        http.mount("https://", adapter)
        http.mount("http://", adapter)
        
        # Include previously failed data
        if MetricsAPI.failed_data:
            data = MetricsAPI.failed_data + data

        try:
            response = http.post(url, data=json.dumps(data), headers=headers)
            response.raise_for_status()
            # Clear failed data if request is successful
            MetricsAPI.failed_data = []
            return response.status_code
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send metrics to web app: {e}")
            # Store failed data
            MetricsAPI.failed_data = data
            return None

    @staticmethod
    def poll_for_message(interval: int = 3):
        """Poll for a message from the web app at regular intervals."""
        logger.info("Beginning polling for messages")
        while True:
            data = requests.get(config.server.url + '/poll_message')
            logger.debug(f"Polling for message: {data.status_code}")
            if data.status_code == 200 and data.json().get("message"):
                _open_win_app(data.json().get("message"))
            sleep(interval)

def _open_win_app(app_name: str):
    if os.name == 'nt':  # For Windows
        try:
            # Sanitize app_name to prevent command injection
            if not app_name.isalnum():
                logger.error("Invalid application name.")
                return

            logger.info(f"Opening {app_name}")
            subprocess.run([app_name])
        except OSError as e:
            if e.winerror == 740:
                logger.error("%s requires administrative privileges to open.", app_name)
            else:
                logger.error("Failed to open %s: %s", app_name, e)
    else:
        logger.error("%s can only be opened on Windows systems.", app_name)
