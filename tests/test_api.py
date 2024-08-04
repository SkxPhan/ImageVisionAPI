def test_healthchecker(test_client):
    response = test_client.get("/api/v1/healthchecker")
    assert response.status_code == 200
    assert response.json() == {"message": "The API is LIVE!!"}


def test_show_about(test_client):
    response = test_client.get("/api/v1/about")
    assert response.status_code == 200


def test_predict(test_client, image_file, mock_image_classifier):
    image_data, filename = image_file
    response = test_client.post(
        "/api/v1/predict/",
        files={"file": (filename, image_data, "image/png")},
    )

    assert response.status_code == 200
    response_data = response.json()

    assert not response_data["error"]
    assert response_data["results"]["filename"] == "test_image.png"
    assert response_data["results"]["width"] == 100
    assert response_data["results"]["height"] == 100
    assert response_data["results"]["prediction"] == "mock_category"
    assert response_data["results"]["probability"] == 0.99
