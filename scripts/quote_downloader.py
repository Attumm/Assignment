import json
import time
import gzip
import urllib3

import requests


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def fetch_and_stream_quotes(url: str, filename: str) -> int:
    max_pages = 1000
    total_quotes = 0
    with gzip.open(filename, 'wt', compresslevel=1) as f:
        for page in range(1, max_pages):
            curren_url = f"{url}?page={page}"
            print(f"\rcurrent: {curren_url}", end=" ", flush=True)
            response = requests.get(curren_url, verify=False)
            try:
                data = response.json()
            except Exception as e:
                print("failed to parse json", e)
                break

            # Unfortunately the API doesn't use status codes.
            if not data['results']:
                break

            total_quotes += len(data['results'])
            json.dump(data['results'],f)
            f.write('\n')

            time.sleep(0.1) # good Netizen

        print("\r")
        return total_quotes


def main(url: str, filename: str):
    print("started quote downloader")
    print(f"downloading quotes from {url}")

    start = time.time()
    total_found = fetch_and_stream_quotes(url, filename)

    print(f"finished quote downloader")
    print(f"total quotes found: {total_found}, time: {round(time.time() - start, 2)}, seconds")


if __name__ == "__main__":
    url = "https://api.quotable.io/quotes/"
    filename = 'quotes.jsonl'

    main(url, filename)
