import pathlib

import pytesseract
from PIL import Image


BASE_DIR = pathlib.Path(__file__).parent
IMAGE_DIR = BASE_DIR / "images"


image_path = IMAGE_DIR / "quote-image-1.png"
image = Image.open(image_path)

predictions_raw = pytesseract.image_to_string(image)
predictions_processed = [x for x in predictions_raw.split("\n")]
print(predictions_processed)
