import os
import requests
import zipfile
import io

def download_driver(target_version="147.0.7727"):
    api_url = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
    response = requests.get(api_url).json()
    
    download_url = None
    for version_data in response['versions']:
        if version_data['version'].startswith(target_version):
            for download in version_data['downloads'].get('chromedriver', []):
                if download['platform'] == 'win64':
                    download_url = download['url']
                    break
    
    if download_url:
        print(f"Найдена ссылка: {download_url}")
        r = requests.get(download_url)
        with zipfile.ZipFile(io.BytesIO(r.content)) as zip_ref:
            for file in zip_ref.namelist():
                if file.endswith("chromedriver.exe"):
                    # Распаковываем без лишних папок
                    filename = os.path.basename(file)
                    with open(os.path.join("driver", filename), "wb") as f:
                        f.write(zip_ref.read(file))
        print("Драйвер успешно обновлен в папке driver/")
    else:
        print("Версия не найдена в API")

if __name__ == "__main__":
    if not os.path.exists("driver"):
        os.makedirs("driver")
    download_driver()