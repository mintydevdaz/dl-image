import os
import sys
from io import BytesIO
from pathlib import Path

import bs4
import requests
import validators
from bs4 import BeautifulSoup
from PIL import Image


def main():
    # Start program
    hello_world()

    # Get valid URL
    url = validate_url()

    # Request URL
    response = get_request(url)

    # Parse HTML
    data = parse(response)

    # Extract src objects from <img> tags
    images = get_soup_image(data[1])

    # Exit if no image URLs extracted
    img_len = len(images)
    image_found(img_len)

    # User choice to exit if 50+ image URLs found
    if img_len >= 50:
        choice(img_len)

    # Create directory on User Desktop
    new_folder = create_folder()

    # Updates Image URLs if webpage built with Shopify
    if check_shopify(data[0]):
        images = shopify_check_http(images)

    # Attempt to download images
    print("Attempting to download images files...")
    dl = download_images(
        url=url,
        images=images,
        filepath=new_folder,
        img_len=img_len
        )

    print(result(image_count=dl,
                 image_num=img_len,
                 filepath=new_folder
                 ))


def hello_world():
    print("-----------------------------------------------------")
    print("Welcome to the Image Download tool")
    print("Press 'Ctrl+c' if the program appears unresponsive.")
    print("-----------------------------------------------------")


def validate_url() -> str:
    url = str(input("Enter URL: "))
    if not validators.url(url):
        sys.exit("Invalid URL. Try again.")
    return url


def get_request(url: str) -> requests.models.Response:
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}  # noqa
        r = requests.get(url, headers=headers, timeout=5)
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        sys.exit(f"Error reaching page! Additional details:\n** {e} **\n")
    except requests.exceptions.Timeout:
        sys.exit("Request timed out. Try again later.")
    return r


def parse(response: requests.models.Response) -> tuple:  # noqa
    # Parse HTML
    soup = BeautifulSoup(response.text, features='lxml')
    # Find all links
    links = soup.findAll('link', href=True)
    # Find image tags
    img = soup.findAll('img')
    return links, img


def get_soup_image(data: bs4.element.ResultSet) -> list[str]:
    img_list = []
    tags = ['src', 'srcset', 'data-src', 'data-srcset', 'data-fallback-src']
    for t in tags:
        for i in data:
            if i.get(t) is not None:
                item = i.get(t)
                img_list.append(item)
    return img_list


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


def download_images(url, images, filepath, img_len):
    image_download_counter = 0
    error_tolerance = int(img_len * 0.2)
    os_error_log = []
    # Attempt to obtain content of image
    for i, image in enumerate(images):

        # Naively check error log. Abort operation at 10:
        if len(os_error_log) == error_tolerance:
            print("**Operation aborted - too many errors found**\nError log:")
            print(*os_error_log, sep='\n')
            if image_download_counter == 0:
                Path(filepath).rmdir()
                print("New folder deleted.")
            sys.exit('-----------------------------------------------------')

        # Combine URL & image strings if http(s) not found
        image = check_http(url, image)

        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}  # noqa

        try:
            # Request bytes content from image URL
            r = requests.get(image, headers=headers).content

            # Check file extension. Force .png if incorrect format.
            ext = check_extension(image)

            # Decode bytes
            try:
                im = Image.open(BytesIO(r))
            except OSError as e:
                os_error_log.append(f" - IMG{i+1}: {e}")
                continue

            # Save File
            filename = f"image{i+1}{ext}"
            path = os.path.join(filepath, filename)

            # TODO - Consider wrapping with try/except
            # Attempt to save to FilePath
            im.save(path)

            # Track number of downloaded images
            image_download_counter += 1

        except Exception as error:
            os_error_log.append(error)
            continue

    return image_download_counter


def check_shopify(links: bs4.element.ResultSet):
    check = [link['href'] for link in links]
    count = sum('shopify' in url for url in check)
    return count > 0


def shopify_check_http(images: list[str]) -> list[str]:
    new_links = []
    for image in images:
        if not image.startswith('http') or not image.startswith('https'):
            image = f"https:{image}"
            new_links.append(image)
    return new_links


def check_http(url: str, image: str) -> str:
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
