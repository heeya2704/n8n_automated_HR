import os
import requests
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def trigger_n8n_test_result_webhook(payload: Dict[str, Any]) -> bool:
    """
    Sends the test result payload to the n8n webhook URL.
    """
    webhook_url = os.getenv(
        "N8N_TEST_RESULT_WEBHOOK_URL", 
        "http://localhost:5678/webhook/test-result"
    )
    
    try:
        logger.info(f"Triggering n8n webhook at {webhook_url} with candidate: {payload.get('candidate_email')}")
        response = requests.post(webhook_url, json=payload, timeout=10)
        if response.status_code in [200, 201, 202]:
            logger.info("Successfully sent payload to n8n webhook")
            return True
        else:
            logger.warning(f"n8n webhook returned status code {response.status_code}: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Failed to connect to n8n webhook: {str(e)}")
        # Return False but allow FastAPI to process locally if needed
        return False
