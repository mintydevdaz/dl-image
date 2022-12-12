import os
import sys
import requests
import validators
from pathlib import Path
from bs4 import BeautifulSoup


def main():
    # Ask user for valid URL
    url = validate_url()

    # Parse HTML
    images = get_url_data(url)

    # !! DELETE
    # print(*images, sep='\n')

    # Exit if no images found.
    img_len = len(images)
    if not img_len:
        sys.exit("No images found on webpage")
    else:
        print(f"Number of images found: {img_len}")

    # Create folder
    new_folder = create_folder()

    # Download image files
    dl = download_images(url=url, images=images, filepath=new_folder)

    # Show results. Delete newly created folder if no images downloaded.
    print(result(image_count=dl,
                 list_of_images=img_len,
                 filepath=new_folder
                 ))


def validate_url():
    # Validate URL input with validators module
    url = str(input("Enter URL: "))
    if not validators.url(url):
        sys.exit("Invalid URL. Try again.")
    return url


def get_url_data(url):
    # Get content of url
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Safari/605.1.15"
            }
        r = requests.get(url, headers=headers, timeout=5)
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        sys.exit(f"Error reaching page: {e}")
    except requests.exceptions.Timeout:
        sys.exit("Request timed out. Try again later.")

    # Parse HTML
    soup = BeautifulSoup(r.text, features='lxml')

    # Find image tags
    extract = soup.findAll(name='img')

    # Get list of images. Exit if error.
    try:
        img_list = [image['src'] for image in extract]
    except KeyError as e:
        sys.exit(f"Can't extract images from webpage. Error: {e}")
    return img_list


def create_folder():
    while True:
        try:
            # Request Folder name
            folder_name = str(input("Enter folder name: "))

            # Points to Desktop regardles of system platform
            parent_dir = str(Path.home() / "Desktop")

            # Check / create final path
            if not os.path.exists(parent_dir):
                sys.exit("Abort operation. Path to desktop not found")
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
        if not image.startswith("https") or not image.startswith("http"):
            image = f"{url}{image}"

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Safari/605.1.15"
                }
            r = requests.get(image, headers=headers).content
            name, ext = os.path.splitext(image)

            # !! DELETE
            # print(name, ext)

            # Manipulate file extensions when image is saved
            html_ext = [
                '.apng', '.gif', '.ico', '.jpg', '.jpeg', '.png', '.svg'
                ]
            if ext == "" or ext not in html_ext:
                ext = ".png"
            elif ext.startswith(".jpeg"):
                ext = ".jpeg"

            try:
                # possibility of decode
                r = str(r, 'utf-8')

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
