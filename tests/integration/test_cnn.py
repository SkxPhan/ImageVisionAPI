import pytest
import torch
from PIL import Image

from app.ml.cnn_model import ImageClassifier


@pytest.mark.integration
def test_invalid_model_path():
    model_path = ""
    categories_path = "tests/data/imagenet_classes.txt"
    with pytest.raises(ValueError):
        ImageClassifier(model_path, categories_path)


@pytest.mark.integration
def test_invalid_categories_path():
    model_path = "tests/data/mobilenet_v3_large.pth"
    categories_path = ""
    with pytest.raises(ValueError):
        ImageClassifier(model_path, categories_path)


@pytest.mark.integration
def test_predict():
    image_path = "tests/data/dog.jpg"
    model_path = "tests/data/mobilenet_v3_large.pth"
    categories_path = "tests/data/imagenet_classes.txt"

    image = Image.open(image_path)

    image_classifier = ImageClassifier(model_path, categories_path)
    probabilities = image_classifier.predict(image)
    max_index = torch.argmax(probabilities)
    assert probabilities.shape == torch.Size([1000])
    assert max_index == 258  # Category: Samoyed
    assert probabilities[max_index] == pytest.approx(0.9736, rel=1e-3)
