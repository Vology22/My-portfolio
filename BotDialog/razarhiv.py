import os
from mega import Mega
from pyunpack import Archive
from typing import List

def download_and_extract_mega_links(links: List[str], output_dir: str = "downloaded_files"):
    os.makedirs(output_dir, exist_ok=True)
    mega = Mega()

    try:
        m = mega.login()  # Анонимный вход
    except Exception as e:
        print(f"Ошибка авторизации в MEGA: {e}")
        return

    for link in links:
        try:
            print(f"Скачивание: {link}")
            file = m.download_url(link, dest_path=output_dir)
            file_path = os.path.join(output_dir, os.path.basename(file))

            if file_path.lower().endswith(('.zip', '.rar', '.7z')):
                print(f"Распаковка: {file_path}")
                Archive(file_path).extractall(output_dir)
        except Exception as e:
            print(f"Ошибка при обработке {link}: {e}")

if __name__ == "__main__":
    links = [
        "https://mega.nz/file/EXAMPLE1#abcdefghijklmnopqrstuvwxyz123456",
        # Добавьте свои ссылки
    ]
    download_and_extract_mega_links(links)
    print("Готово!")