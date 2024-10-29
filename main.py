import os
import requests
from bs4 import BeautifulSoup
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
}

urls = [
    "https://dam.gov.bd/site/page/77c3d769-4cc5-43a4-bb9d-c82e51fdc292",
    "https://dam.gov.bd/site/page/5b91ee24-2ea4-4411-8db2-93dd1db77503"
]

base_download_dir = "downloads"
os.makedirs(base_download_dir, exist_ok=True)


def scrape_pdfs(url):
    url_dir = url.replace("https://", "").replace("http://", "").replace("/", "_")
    output_dir = os.path.join(base_download_dir, url_dir)
    os.makedirs(output_dir, exist_ok=True)

    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        pdf_links = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if re.search(r"\.pdf$", href):
                print(href)
                clean_url = re.sub(r"/\.\./", "/", href)

                if clean_url.startswith("http"):
                    pdf_links.append(clean_url)
                else:
                    pdf_links.append("https://dam.gov.bd" + clean_url)

        for pdf_url in pdf_links:
            download_pdf(pdf_url, output_dir)

    except requests.RequestException as e:
        print(f"Failed to retrieve {url}: {e}")


def download_pdf(pdf_url, output_dir):
    try:
        pdf_name = pdf_url.split("/")[-1]
        pdf_path = os.path.join(output_dir, pdf_name)

        pdf_url = pdf_url.replace('https://dam.gov.bd//dam.portal.gov.bd/uploader/server/', 'https://dam.portal.gov.bd/')

        print(f"Downloading {pdf_url}...")
        pdf_response = requests.get(pdf_url, headers=headers, verify=False)
        pdf_response.raise_for_status()

        with open(pdf_path, "wb") as pdf_file:
            pdf_file.write(pdf_response.content)
        print(f"Saved to {pdf_path}")

    except requests.RequestException as e:
        print(f"Failed to download {pdf_url}: {e}")


for url in urls:
    scrape_pdfs(url)
