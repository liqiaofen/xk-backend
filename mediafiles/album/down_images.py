import shutil  # to save it locally
from time import sleep

import requests  # to get image from the web


def download(j, index):
    # Set up the image URL and filename
    image_url = f"https://picsum.photos/seed/{j}-{index}/200/300"
    filename = f'D:/qiaofinn/xk-backend/media/album/{j}-{index}.jpg'
    sleep(1)
    # Open the url image, set stream to True, this will return the stream content.
    r = requests.get(image_url, stream=True)

    # Check if the image was retrieved successfully
    if r.status_code == 200:
        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        r.raw.decode_content = True

        # Open a local file with wb ( write binary ) permission.
        with open(filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

        print('Image sucessfully Downloaded: ', filename)
    else:
        print('Image Couldn\'t be retreived')


# for j in range(1, 8):
#     for i in range(0, 2):
#         download(j, i)

for i in range(30, 40):
    download(0, i)
