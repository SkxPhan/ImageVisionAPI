import torch
from torchvision import transforms, models
from PIL import Image


class Preprocessor(torch.nn.Module):
    def __init__(self):
        super(Preprocessor, self).__init__()
        self._transform = transforms.Compose(
            [
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )

    def forward(self, x):
        return self._transform(x)


class ImageClassifier:
    def __init__(
        self, model_path, categories_path="imagenet_classes.txt", device=None
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

        self._categories = self._load_categories(categories_path)

    def _load_model(self, model_path):
        try:
            self._model.load_state_dict(torch.load(model_path))
        except FileNotFoundError:
            raise ValueError(f"Model file not found: {model_path}")
        except Exception as e:
            raise RuntimeError(f"Error loading model: {e}")

    def _load_categories(self, categories_path):
        try:
            with open(categories_path, "r") as f:
                return [s.strip() for s in f.readlines()]
        except FileNotFoundError:
            raise ValueError(f"Categories file not found: {categories_path}")
        except Exception as e:
            raise RuntimeError(f"Error loading categories: {e}")

    def predict(self, image_path):
        image = Image.open(image_path)
        input_tensor = self._preprocessor(image).unsqueeze(0).to(self._device)

        with torch.no_grad():
            output = self._model(input_tensor)

        probabilities = torch.nn.functional.softmax(output[0], dim=0)
        return probabilities

    def top_k_predictions(self, probabilities, k=5):
        top_prob, top_catid = torch.topk(probabilities, k)
        return [
            (self._categories[catid], prob.item())
            for prob, catid in zip(top_prob, top_catid)
        ]

    def predict_category(self, image_path):
        probabilities = self.predict(image_path)
        top_2_predictions = self.top_k_predictions(probabilities, 2)
        threshold_mul = 2
        if top_2_predictions[0][1] > top_2_predictions[1][1] * threshold_mul:
            return (top_2_predictions[0][0], top_2_predictions[0][1])
        else:
            return ("Unknown", None)


def main():
    image_file = "dog.jpg"
    model_path = "mobilenet_v3_large.pth"

    # Initialize the classifier
    classifier = ImageClassifier(model_path)

    # Perform prediction
    probabilities = classifier.predict(image_file)

    # Get top 5 predictions
    top_predictions = classifier.top_k_predictions(probabilities, k=5)

    # Print results
    for category, prob in top_predictions:
        print(f"{category}: {prob:.4f}")

    # Print the category directly
    category, prob = classifier.predict_category(image_file)
    print(f"This is a {category} (probability: {prob:.4f})")


if __name__ == "__main__":
    main()
