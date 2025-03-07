import json
import logging
import requests
from config import config

logger = logging.getLogger(__name__)

class MetricsAPI:
    @staticmethod
    def send_metrics(data: list):
        # API to send metrics data to the web app
        url = config.server.url + '/store_metrics'
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(url, data=json.dumps(data), headers=headers)
            response.raise_for_status()
            return response.status_code
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send metrics to web app: {e}")
            return None
