"""
This script is created for downloading books from codernet.ru online library.
Just place this script to the directory where you want to get the books
and run it with Python >= 3.6. You can also give it another path.
"""

import os
import requests
import urllib
from bs4 import BeautifulSoup

URL = 'https://codernet.ru/media/'
FOLDER = os.path.dirname(os.path.realpath(__file__))


def download_file(file_url: str, file_path: str) -> bool:
    if os.path.isfile(file_path):
        return False
    response = requests.get(file_url)
    response.raise_for_status()
    with open(file_path, 'wb') as f:
        f.write(response.content)
    return True


def ensure_dir(file_path: str) -> None:
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


def get_pdf_links(href):
    book_url = f'{URL}{href}'
    response = requests.get(book_url)
    response.raise_for_status()
    html = BeautifulSoup(response.content, 'html5lib')
    return [
        a['href'] for a in html.find_all('a')
        if '.pdf' in a['href']
    ]


def download_books(hrefs: list, folder: str) -> tuple:
    errors = []
    downloaded = 0
    for href in hrefs:
        try:
            pdf_links = get_pdf_links(href)
        except Exception:
            continue
        dir_name = urllib.parse.unquote(href.strip('/'))
        dir_path = f'{folder}{dir_name}'
        for pdf in pdf_links:
            file_name = urllib.parse.unquote(pdf.split('/')[-1])
            file_path = f'{dir_path}/{file_name}'
            ensure_dir(file_path)
            file_url = f'{URL}{href}/{pdf}'
            try:
                success = download_file(file_url, file_path)
                if success:
                    downloaded += 1
            except Exception as e:
                errors.append({
                    'file_url': file_url,
                    'file_path': file_path,
                    'error_message': str(e)
                })
    return downloaded, errors


def get_books_hrefs(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html5lib')
    return [a['href'] for a in soup.find_all('a')]


def main():
    folder = input(
        'Give me the path or leave it empty'
        'to use default directory: '
    ) or FOLDER
    folder = f'{folder.rstrip("/")}/'
    try:
        hrefs = get_books_hrefs(URL)
    except Exception as e:
        print(f'Cannot access the books list: {str(e)}')
        exit()
    print(f'{len(hrefs)} books found.')
    downloaded, errors = download_books(hrefs, folder)
    print(f'Done, downloaded {downloaded} books.')
    if errors:
        print(f'Errors found: {errors}')


if __name__ == '__main__':
    main()
