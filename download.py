import os
import sys
import requests
from bs4 import BeautifulSoup
from pathlib import Path


def main():
    # Ask User for valid URL
    url = str(input("Enter URL: "))

    # Parse HTML
    images = get_url(url)

    # Check if any images found
    if not len(images):
        sys.exit("No images found on webpage")

    # Create folder
    path = create_folder(images)

    # Show total no. of images found
    print(f"Number of Images Found: {len(images)}")

    # Download image files
    num = download(images, path)

    # Show total images downloaded
    if num == len(images):
        print("All images downloaded!")
    else:
        print(f"Total images downloaded: {num}")

    # Delete folder if no images downloaded
    if num == 0:
        Path(path).rmdir()
        print("No images downloaded. Folder removed.")


def get_url(url):
    # Content of URL
    r = requests.get(url)
    # Exit if response is not 200
    if r.status_code != 200:
        sys.exit(f"Error reaching page. Status code: {r.status_code}")
    # Parse HTML code
    soup = BeautifulSoup(r.text, features='lxml')
    # Find all Images in URL
    extract = soup.findAll(name='img')
    # Return list of image objects
    try:
        img_list = [image['src'] for image in extract]
    except KeyError as e:
        sys.exit(f"Can't extract images from webpage. Error: {e}")
    return img_list


def create_folder(images):
    while True:
        try:
            # Request Folder name
            folder_name = str(input("Enter folder name: "))
            # Point to Downloads folder
            parent_dir = str(Path.home() / "Downloads")
            # Create final path
            path = os.path.join(parent_dir, folder_name)
            # Create folder
            os.mkdir(path)
            return path
        except OSError as e:
            print(e)
            continue


def download(images, path):
    count = 0
    for i, image in enumerate(images):
        # Attempt to obtain content of image
        try:
            r = requests.get(image).content
            name, ext = os.path.splitext(image)
            # Force .png file extension if none present
            if ext == "":
                ext = ".png"
            try:
                # possibility of decode
                r = str(r, 'utf-8')
            except UnicodeDecodeError:
                # Download image after checking above condition
                with open(f"{path}/image{i+1}{ext}", "wb+") as f:
                    f.write(r)
                # Track number of downloaded images
                count += 1
        except Exception:
            continue
    return count


if __name__ == "__main__":
    main()
