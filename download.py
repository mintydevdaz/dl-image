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
    print(*images, sep='\n')

    # Exit if no images found.
    img_len = len(images)
    if not img_len:
        sys.exit("No images found on webpage")
    else:
        print(f"Number of images found: {img_len}")

    # Create folder
    new_folder = create_folder()

    # Download image files
    dl = download_images(images=images, filepath=new_folder)

    # Show results. Delete newly created folder if no images downloaded.
    r = result(image_count=dl,
               list_of_images=img_len,
               filepath=new_folder
               )
    print(r)


def validate_url():
    url = str(input("Enter URL: "))
    if not validators.url(url):
        sys.exit("Invalid URL. Try again.")
    return url


def get_url_data(url):
    # Content of URL
    r = requests.get(url)

    # Exit if response is not 200
    if r.status_code != 200:
        sys.exit(f"Error reaching page. Status code: {r.status_code}")

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
            # Point to 'Downloads' folder on Mac
            parent_dir = str(Path.home() / "Downloads")
            # Create final path
            path = os.path.join(parent_dir, folder_name)
            # Create folder
            os.mkdir(path)
            return path
        except OSError as e:
            print(e)
            continue


def download_images(images, filepath):
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
        return "All images downloaded!"
    else:
        return f"Total images downloaded: {image_count}"


if __name__ == "__main__":
    main()
