import requests
from PIL import Image

from app.main import BASE_DIR
from config import get_settings


ENDPOINT = "https://digitalocean-fastapi.app/"


# client = TestClient(app)  # we won't use it in production tests - use ENDPOINT of a deployed app instead


def test_invalid_file_upload_error():
    response = requests.post(ENDPOINT)
    assert response.status_code == 422
    assert "application/json" in response.headers["Content-Type"]


def test_prediction():
    settings = get_settings()
    saved_images_path = BASE_DIR / "images"
    for file_path in saved_images_path.glob("*"):
        try:
            image = Image.open(file_path)
        except:
            image = None

        response = requests.post(ENDPOINT,
                               files={"file": open(file_path, "rb")},
                               headers={"Authorization": f"JWT {settings.app_auth_token_prod}"}  # prod token used instead of dev token
                               )
        if image is None:
            assert response.status_code == 400
        else:
            assert response.status_code == 200
            data = response.json()
            assert len(data.keys()) == 2


def test_prediction_missing_headers():
    saved_images_path = BASE_DIR / "images"
    for file_path in saved_images_path.glob("*"):
        try:
            image = Image.open(file_path)
        except:
            image = None

        response = requests.post(ENDPOINT,
                               files={"file": open(file_path, "rb")},
                               )
        assert response.status_code == 401
