import os
import sys
import requests
import validators
import bs4
from pathlib import Path
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup


def main():
    # Get valid URL
    url = validate_url()

    # Request URL
    response = get_request(url)

    # Parse HTML
    extract = parse_request(response)

    # Extract src objects from <img> tags
    images = get_soup_image(extract)

    # Exit if no image URLs extracted
    img_len = len(images)
    image_found(img_len)

    # User choice to exit if 50+ image URLs found
    if img_len >= 50:
        choice(img_len)

    # Create directory on User Desktop
    new_folder = create_folder()

    dl = download_images(url=url, images=images, filepath=new_folder)

    print(result(image_count=dl,
                 image_num=img_len,
                 filepath=new_folder
                 ))


def validate_url() -> str:
    '''Validates URL input from User'''
    url = str(input("Enter URL: "))
    if not validators.url(url):
        sys.exit("Invalid URL. Try again.")
    return url


def get_request(url: str) -> requests.models.Response:
    '''
    Attempts to get response from URL. Exits program if page can't be reached. Exits program if there's a request timeout.

    :param url: URL
    :type url: str
    :return: requests object
    :rtype: requests.models.Response
    '''
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}  # noqa
        r = requests.get(url, headers=headers, timeout=5)
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        sys.exit(f"Error reaching page! Additional details:\n** {e} **\n")
    except requests.exceptions.Timeout:
        sys.exit("Request timed out. Try again later.")
    return r


def parse_request(response: requests.models.Response) -> bs4.element.ResultSet:
    '''
    Finds and returns image tags

    :param response: requests.get object
    :type response: requests.models.Response
    :return: Beautiful Soup object with html <img> tags
    :rtype: bs4.element.ResultSet
    '''
    # Parse HTML
    soup = BeautifulSoup(response.text, features='lxml')
    # Find image tags
    return soup.findAll('img')


def get_soup_image(extract: bs4.element.ResultSet) -> list[str]:
    '''Extract URLs from <img> tags'''
    # sourcery skip: for-append-to-extend, use-contextlib-suppress
    image_src_list = []
    tags = ['src', 'srcset', 'data-src', 'data-srcset', 'data-fallback-src']
    for tag in tags:
        try:
            for img in extract:
                image_src_list.append(img[tag])
        except Exception:
            pass

        if image_src_list:
            break
        else:
            continue

    return image_src_list


def image_found(img_len: int):
    '''Exit if no images found else print image count to terminal'''
    if not img_len:
        sys.exit("Unable to grab images from website.")
    else:
        print(f"Number of images found: {img_len}")


def choice(img_len: int):
    '''Prompt User to exit program if too many images found'''
    while True:
        try:
            decision = str(input(
                "High volume of images found. Continue (y/n)? "
            )).lower()
            if decision in {'n', 'no'}:
                sys.exit("User decided to terminate program.")
            elif decision in {'y', 'yes'}:
                break
            else:
                continue
        except Exception:
            continue


def create_folder() -> str:
    '''
    Create new folder in Desktop directory. Exit if Desktop path not found.
    Continue prompt if filename already exists on Desktop.

    :return: file path to Desktop
    :rtype: str
    '''
    while True:
        try:
            # Request Folder name
            folder_name = str(input("Enter folder name: "))

            # Points to Desktop regardless of system platform
            parent_dir = str(Path.home() / "Desktop")

            # Check / create final path
            if not os.path.exists(parent_dir):
                sys.exit("Operation aborted. Path to desktop not found")
            else:
                path = os.path.join(parent_dir, folder_name)

            # Create folder
            os.mkdir(path)
            return path

        # Raise error if folder name already exists
        except OSError as e:
            print(e)
            continue


def download_images(url, images, filepath):
    count = 0
    # Attempt to obtain content of image
    for i, image in enumerate(images):

        # Combine URL & image strings if http(s) not found
        image = check_http(url, image)

        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}  # noqa

        try:
            r = requests.get(image, headers=headers, timeout=1).content
        except Exception:
            continue

        # Check file extension. Force .png if incorrect format.
        ext = check_extension(image)

        # Open Image
        try:
            im = Image.open(BytesIO(r))
        except Exception:
            continue

        # Save File
        filename = f"image{i+1}{ext}"
        path = os.path.join(filepath, filename)
        try:
            im.save(path)
        except Exception:
            continue

        # Track number of downloaded images
        count += 1

    return count


def check_http(url: str, image: str) -> str:
    '''Modifies image URL if HTTP not present'''
    if not image.startswith("http") or not image.startswith("https"):
        return f"{url}{image}"
    else:
        return image


def check_extension(image: str) -> str:
    '''Modifies file extension if formatted incorrectly'''
    name, ext = os.path.splitext(image)
    html_ext = ['.apng', '.gif', '.ico', '.jpg', '.jpeg', '.png', '.svg']
    if ext == "" or ext not in html_ext:
        ext = ".png"
    return ext


def result(image_count: int, image_num: int, filepath: str) -> str:
    '''Prints final result of program to Command-Line'''

    # Delete folder if no images downloaded
    if image_count == 0:
        Path(filepath).rmdir()
        return "Unable to download images. New folder deleted."

    # Show total images downloaded
    if image_count == image_num:
        return f"All images downloaded!\nFiles saved in: {filepath}"
    else:
        return f"Images downloaded: {image_count}\nFiles saved in: {filepath}"


if __name__ == "__main__":
    main()
