import requests
import time

def get_api(url, max_retries=3):
    import time
    for tentative in range(max_retries):
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.Timeout:
            print(f"Timeout — tentative {tentative+1}/{max_retries}")
            time.sleep(2)
        except requests.exceptions.HTTPError as e:
            print(f"Erreur HTTP {e.response.status_code}")
            return None
    return None