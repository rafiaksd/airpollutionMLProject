import os
import requests
import time
import base64
from io import BytesIO
from PIL import Image

images_url_txt = 'nightPoll2image_urls.txt'  # Text file containing URLs or base64 data
folder_name = 'pollution_night'

def tryImg64(base64_string, file_path):
    """Decodes a base64 string to an image and saves it to a file."""
    try:
        # Remove the 'data:image/jpeg;base64,' part of the string if it exists
        if base64_string.startswith("data:image"):
            base64_string = base64_string.split(",")[1]

        # Decode the base64 string
        image_data = base64.b64decode(base64_string)

        # Convert the byte data to an image using PIL
        image = Image.open(BytesIO(image_data))

        # Save the image to the specified file path
        image.save(file_path)
        print(f"Image saved as {file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

def download_image(url, folder, index):
    """Function to download and save image from a URL."""
    try:
        # Ensure the folder exists
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        # Send a GET request to the image URL
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Generate image filename (image1.jpg, image2.jpg, etc.)
            image_filename = os.path.join(folder, f"{folder}_image{index}.jpg")
            
            # Write the image to the file
            with open(image_filename, 'wb') as file:
                file.write(response.content)
            print(f"Downloaded {image_filename}")
            return True
        else:
            print(f"Failed to retrieve image from URL: {url}")
            return False
    except Exception as e:
        print(f"Error downloading image from {url}: {e}")
        return False

index = 1
success = 0
fail = 0

start = time.time()
# Open the file in read mode
with open(images_url_txt, 'r') as file:
    # Iterate through each line in the file
    for line in file:
        line = line.strip()
        if line.startswith("data:image"):  # Check if line is base64-encoded
            # Handle base64 image data
            base64_string = line
            image_filename = os.path.join(folder_name, f"{folder_name}_image{index}.jpg")
            tryImg64(base64_string, image_filename)  # Decode and save base64 image
            success += 1
        else:
            # Download image from URL
            if download_image(line, folder_name, index):
                success += 1
            else:
                fail += 1
        index += 1

end = time.time()
time_took = (end - start)
print(f'Download finished! Downloaded: {success} Failed: {fail} | Time: {time_took}')
