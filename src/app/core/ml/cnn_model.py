import torch
from PIL import Image
from torchvision import models, transforms


class Preprocessor(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self._transform = transforms.Compose(
            [
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],  # Specific mean to the model
                    std=[0.229, 0.224, 0.225],  # Specific std to the model
                ),
            ]
        )

    def forward(self, x):
        return self._transform(x)


class ImageClassifier:
    def __init__(
        self,
        model_path,
        label_path,
        device=None,
    ):
        self._preprocessor = Preprocessor()

        self._device = (
            device
            if device
            else ("cuda" if torch.cuda.is_available() else "cpu")
        )
        self._model = models.mobilenet_v3_large()
        self._load_model(model_path)
        self._model.to(self._device)
        self._model.eval()

        self._categories = self._load_categories(label_path)

    def _load_model(self, model_path):
        try:
            self._model.load_state_dict(
                torch.load(model_path, weights_only=True)
            )
        except FileNotFoundError:
            raise ValueError(f"Model file not found: {model_path}")

    def _load_categories(self, label_path):
        try:
            with open(label_path) as f:
                return [s.strip() for s in f.readlines()]
        except FileNotFoundError:
            raise ValueError(f"Categories file not found: {label_path}")

    def predict(self, image):
        input_tensor = self._preprocessor(image).unsqueeze(0).to(self._device)

        with torch.no_grad():
            output = self._model(input_tensor)

        probabilities = torch.nn.functional.softmax(output[0], dim=0)
        return probabilities

    def top_k_predictions(self, image, k=5):
        probabilities = self.predict(image)
        top_prob, top_cat_id = torch.topk(probabilities, k)
        return [
            (self._categories[cat_id], prob.item())
            for prob, cat_id in zip(top_prob, top_cat_id)
        ]

    def predict_category(self, image):
        top_2_predictions = self.top_k_predictions(image, 2)
        threshold_mul = 2
        if top_2_predictions[0][1] > top_2_predictions[1][1] * threshold_mul:
            return (top_2_predictions[0][0], top_2_predictions[0][1])
        else:
            return ("Unknown", None)


def main():  # pragma: no cover
    image_file = "dog.jpg"
    model_path = "mobilenet_v3_large.pth"
    label_path = "imagenet_classes.txt"

    # Initialize the classifier
    classifier = ImageClassifier(model_path, label_path)

    # Perform prediction
    image = Image.open(image_file)
    probabilities = classifier.predict(image)

    # Get top 5 predictions
    top_predictions = classifier.top_k_predictions(probabilities, k=5)

    # Print results
    for category, prob in top_predictions:
        print(f"{category}: {prob:.4f}")

    # Print the category directly
    category, prob = classifier.predict_category(image)
    print(f"This is a {category} (probability: {prob:.4f})")


if __name__ == "__main__":  # pragma: no cover
    main()
