import pytest
import torch

from app.ml.cnn_model import ImageClassifier, Preprocessor


@pytest.fixture
def mock_image_classifier(monkeypatch):
    def mock_init(self, *args, **kwargs):
        self._categories = ["cat", "dog", "car", "plane", "boat"]

    monkeypatch.setattr(ImageClassifier, "__init__", mock_init)

    def mock_predict(*args, **kwargs):
        return torch.tensor([0.0098, 0.0494, 0.8500, 0.0788, 0.012])

    monkeypatch.setattr(ImageClassifier, "predict", mock_predict)


@pytest.mark.unit
def test_preprocessor(image):
    preprocessor = Preprocessor()
    torch_image = preprocessor(image)
    assert torch_image.shape == (3, 224, 224)
    assert torch.is_tensor(torch_image)


@pytest.mark.unit
def test_top_k_predictions(mock_image_classifier, image):
    image_classifier = ImageClassifier()
    predictions = image_classifier.top_k_predictions(image, 3)
    assert len(predictions) == 3

    expected_prediction = [("car", 0.8500), ("plane", 0.0788), ("dog", 0.0494)]
    for (label, prob), (expected_label, expected_prob) in zip(
        predictions, expected_prediction
    ):
        assert label == expected_label
        assert prob == pytest.approx(expected_prob, rel=1e-3)


@pytest.mark.unit
def test_predict_category(mock_image_classifier, image):
    image_classifier = ImageClassifier()
    prediction = image_classifier.predict_category(image)
    label, prob = prediction
    assert label == "car"
    assert prob == pytest.approx(0.8500, rel=1e-3)
