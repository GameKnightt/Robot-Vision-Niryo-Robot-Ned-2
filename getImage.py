import requests
import numpy as np
import cv2
from io import BytesIO

# Server URL
IP = "172.21.182.17" # IP of the Raspberry Pi
PORT = "8000" # Port of the server
server_url = f"http://{IP}:{PORT}/image.jpg"

# Define a dictionary to set the "no-proxy" option
proxies = {
    'http': None,
    'https': None,
}

# Make an HTTP GET request to the server to get the image
print(f"Sending GET request to {server_url}...")
response = requests.get(server_url, proxies=proxies)

if response.status_code == 200:
    # Read the image data into a NumPy array
    image_data = np.frombuffer(response.content, dtype=np.uint8)

    # Decode the image using OpenCV
    image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

    # Display the image (or perform further processing)
    cv2.imshow('Captured Image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print(f"Failed to retrieve the image. HTTP status code: {response.status_code}")
