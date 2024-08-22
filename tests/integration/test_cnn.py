import pytest
import torch
from PIL import Image

from app.ml.cnn_model import ImageClassifier


@pytest.fixture
def model_path():
    return "tests/data/mobilenet_v3_large.pth"


@pytest.fixture
def categories_path():
    return "tests/data/imagenet_classes.txt"


@pytest.mark.integration
def test_load_model(model_path, categories_path):
    image_classigier = ImageClassifier(model_path, categories_path)
    assert image_classigier._model is not None
    assert image_classigier._categories is not None


@pytest.mark.integration
@pytest.mark.parametrize(
    "model_path, categories_path, expected_exception",
    [
        ("tests/data/mobilenet_v3_large.pth", "", ValueError),
        ("", "tests/data/imagenet_classes.txt", ValueError),
        ("", "", ValueError),
    ],
)
def test_fail_load_model(model_path, categories_path, expected_exception):
    with pytest.raises(expected_exception):
        ImageClassifier(model_path, categories_path)


@pytest.mark.integration
def test_predict(model_path, categories_path):
    image_path = "tests/data/dog.jpg"

    image_classifier = ImageClassifier(model_path, categories_path)
    image = Image.open(image_path)

    probabilities = image_classifier.predict(image)
    max_index = torch.argmax(probabilities)
    assert probabilities.shape == torch.Size([1000])
    assert max_index == 258  # Category: Samoyed
    assert probabilities[max_index] == pytest.approx(0.9736, rel=1e-3)
