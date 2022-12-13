import os
import sys
import requests
import validators
from pathlib import Path
from bs4 import BeautifulSoup


def main():
    # Ask user for valid URL
    url = str(input("Enter URL: "))
    valid_url = validate_url(url)

    # Parse HTML
    extract = get_url_data(valid_url)

    # Get list of images
    images = get_soup_image(extract)

    # Exit if no images found.
    img_len = len(images)
    if not img_len:
        sys.exit("Unable to grab images from website.")
    else:
        print(f"Number of images found: {img_len}")

    # Ask user if they'll continue if high volume of images found
    if img_len >= 50:
        choice(img_len)

    # Create folder
    new_folder = create_folder()

    # Download image files
    dl = download_images(url=url, images=images, filepath=new_folder)

    # Show results. Delete newly created folder if no images downloaded.
    print(result(image_count=dl,
                 list_of_images=img_len,
                 filepath=new_folder
                 ))


def validate_url(url):
    if not validators.url(url):
        sys.exit("Invalid URL. Try again.")
    return url


def get_url_data(url):
    try:
        # Get content of url
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"} # noqa
        r = requests.get(url, headers=headers, timeout=5)
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        sys.exit(f"Error reaching page! Additional details:\n**{e}**\n")
    except requests.exceptions.Timeout:
        sys.exit("Request timed out. Try again later.")

    # Parse HTML
    soup = BeautifulSoup(r.text, features='lxml')

    # Find image tags
    return soup.findAll('img')


def get_soup_image(extract):
    # Get list of images. Exit if error.
    img_1 = []
    img_2 = []
    img_3 = []
    img_4 = []
    try:
        img_1 = [image['src'] for image in extract]
    except Exception:
        try:
            img_2 = [image['data-src'] for image in extract]
        except Exception:
            try:
                img_3 = [image['data-srcset'] for image in extract]
            except Exception:
                try:
                    img_4 = [image['data-fallback-src'] for image in extract]
                except Exception:
                    pass
    return img_1 + img_2 + img_3 + img_4


def choice(img_len):
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


def create_folder():
    while True:
        try:
            # Request Folder name
            folder_name = str(input("Enter folder name: "))

            # Points to Desktop regardles of system platform
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

        # Combine URL & image strings if http/s not found
        if not image.startswith("http") or not image.startswith("https"):
            image = f"{url}{image}"

        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"} # noqa
            r = requests.get(image, headers=headers).content
            name, ext = os.path.splitext(image)

            # Check file extension. Force .png if incorrect format.
            html_ext = [
                '.apng', '.gif', '.ico', '.jpg', '.jpeg', '.png', '.svg'
            ]
            if ext == "" or ext not in html_ext:
                ext = ".png"

            try:
                # possibility of decode
                r = str(r, encoding='utf-8')

            except UnicodeDecodeError:
                # Download image after checking above condition
                with open(f"{filepath}/image{i+1}{ext}", "wb+") as f:
                    f.write(r)

                # Track number of downloaded images
                count += 1

        except Exception:
            continue

    return count


def result(image_count, list_of_images, filepath):
    # Delete folder if no images downloaded
    if image_count == 0:
        Path(filepath).rmdir()
        return "Unable to download images. New folder deleted."

    # Show total images downloaded
    if image_count == list_of_images:
        return f"All images downloaded!\nFiles saved in: {filepath}"
    else:
        return f"Images downloaded: {image_count}\nFiles saved in: {filepath}"


if __name__ == "__main__":
    main()
