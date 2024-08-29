import pytest
import torch

from app.core.ml.cnn_model import ImageClassifier, Preprocessor


@pytest.fixture(scope="function")
def mocked_image_classifier(monkeypatch):
    def mock_init(self, *args, **kwargs):
        self._categories = ["cat", "dog", "car", "plane", "boat"]

    monkeypatch.setattr(ImageClassifier, "__init__", mock_init)

    def mock_predict(*args, **kwargs):
        return torch.tensor([0.0098, 0.0494, 0.8500, 0.0788, 0.012])

    monkeypatch.setattr(ImageClassifier, "predict", mock_predict)

    return ImageClassifier(model_path=None, label_path=None)


@pytest.mark.unit
def test_preprocessor(image):
    preprocessor = Preprocessor()
    torch_image = preprocessor(image)
    assert torch_image.shape == (3, 224, 224)
    assert torch.is_tensor(torch_image)


@pytest.mark.unit
def test_top_k_predictions(mocked_image_classifier, image):
    predictions = mocked_image_classifier.top_k_predictions(image, 3)
    assert len(predictions) == 3

    expected_prediction = [("car", 0.8500), ("plane", 0.0788), ("dog", 0.0494)]
    for (label, prob), (expected_label, expected_prob) in zip(
        predictions, expected_prediction
    ):
        assert label == expected_label
        assert prob == pytest.approx(expected_prob, rel=1e-3)


@pytest.mark.unit
def test_predict_category(mocked_image_classifier, image):
    prediction = mocked_image_classifier.predict_category(image)
    label, prob = prediction
    assert label == "car"
    assert prob == pytest.approx(0.8500, rel=1e-3)


@pytest.mark.unit
def test_fail_predict_category(mocked_image_classifier, image, monkeypatch):
    def mock_predict(*args, **kwargs):
        return torch.tensor([0.5, 0.5])

    monkeypatch.setattr(mocked_image_classifier, "predict", mock_predict)

    prediction = mocked_image_classifier.predict_category(image)
    label, prob = prediction
    assert label == "Unknown"
    assert prob is None
