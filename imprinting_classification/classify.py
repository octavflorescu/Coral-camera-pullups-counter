# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""A demo to classify image."""

import argparse
from edgetpu.classification.engine import ClassificationEngine
from edgetpu.utils import dataset_utils
from PIL import Image


class Classifier:
    def __init__(self, using_model: str, label_file: str):
        # Prepare labels.
        self.labels = dataset_utils.read_label_file(label_file)
        # Initialize engine.
        self.engine = ClassificationEngine(using_model)

    def classify(self, image: Image, top_k=3):
        return self.engine.classify_with_image(image, top_k=top_k)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--model', help='File path of Tflite model.', required=True)
    parser.add_argument('--label', help='File path of label file.', required=True)
    parser.add_argument(
        '--image', help='File path of the image to be recognized.', required=True)
    args = parser.parse_args()

    # Run inference.
    classifier = Classifier(using_model=args.model, label_file=args.label)
    classification_result = classifier.classify(image=Image.open(args.image))

    for result in classification_result:
        print('---------------------------')
        print(classifier.labels[result[0]])
        print('Score : ', result[1])


if __name__ == '__main__':
    main()
