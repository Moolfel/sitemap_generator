from main import app
from flask_api import status

import io
import os


class TestMain:
    def test__load_data__invalid_route(self):
        """Tests that loading file on invalid route fails"""
        with app.test_client() as client:

            csv_file = "input.csv"
            file_path = os.path.join('config', csv_file)
            with open(file_path, 'rb') as upload_file:
                test_file = (io.BytesIO(upload_file.read()), 'input.csv', 'text/csv')

            file = {
                'file': test_file
                }
            invalid_route = '/aaabbb'
            response = client.post(
                invalid_route, data=file,
                content_type='multipart/form-data')

            assert response.status_code == status.HTTP_404_NOT_FOUND

    def test__load_data(self):
        """Test that loading data succeed."""
        with app.test_client() as client:
            csv_file = "input.csv"
            file_path = os.path.join('config', csv_file)
            with open(file_path, 'rb') as upload_file:
                test_file = (io.BytesIO(upload_file.read()), 'input.csv', 'text/csv')

            file = {
                'file': test_file
                }
            response = client.post(
                '/load', data=file,
                content_type='multipart/form-data')

            assert response.status_code == status.HTTP_200_OK
