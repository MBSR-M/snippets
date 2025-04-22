import requests
import json
import logging
from concurrent.futures import ThreadPoolExecutor


def setup_logging():
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )


def send_request(session, url, headers, json_data, request_id):
    try:
        response = session.post(url, headers=headers, data=json_data)
        logging.info(f"Request {request_id}: Status {response.status_code}, Response: {response.text}")
    except requests.RequestException as e:
        logging.error(f"Request {request_id} failed: {e}")


def main():
    url = "https://itg-in-02.dev.cyanconnode.com/probussamples"
    headers = {
        "accept": "application/json",
        "Authorization": "Basic cHJvYnVzZGF0YWNvbGxlY3Rvcjp5WkxOaE9pZVlBTXRSTGRC",
        "X-API-Key": "K5RtJNDRXf1hPXPP3UvL6a",
        "Content-Type": "application/json"
    }

    data = [
        {
            "dvcIdN": "string",
            "mobAppDataUniqueId": "string",
            "userId": "string",
            "dataSource": "BLUETOOTH",
            "remarks": "string",
            "exportDTTM": "2025-02-27T12:03:48.485Z",
            "MeterDTTM": "2025-02-27T12:03:48.485Z",
            "phase": "string",
            "profileCode": "1.0.99.2.0.255",
            "preVEE": [
                {
                    "enQty": "string",
                    "attribute": 0,
                    "RegisterID": "string"
                }
            ]
        }
    ]
    json_data = json.dumps(data)
    num_requests = 2
    max_workers = 10

    setup_logging()

    with requests.Session() as session, ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(send_request, session, url, headers, json_data, i + 1) for i in range(num_requests)]
        for future in futures:
            future.result()


if __name__ == "__main__":
    main()
