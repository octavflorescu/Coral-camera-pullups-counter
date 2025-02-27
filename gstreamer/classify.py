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

"""A demo which runs object classification on camera frames."""
import re
import imp
import os
import gstreamer
import numpy
import signal
import operator
from PIL import Image
from PIL import ImageDraw, ImageFont
from typing import Tuple, Union
from definitions import CONSTANTS
import sys
sys.path.append(os.path.abspath('/home/mendel/mnt/cameraSamples/examples-camera/'))
from imprinting_classification.classify import Classifier

try:
    from .VideoWriter import *
    from .FaceDetector import *
except Exception:  # ImportError
    from VideoWriter import *
    from FaceDetector import *

class Main:
    def __init__(self):
        # self.t0 = time.time()  # timer used for debugging the video's fps
        signal.signal(signal.SIGINT, self.sigint_handler)
        # reduce the video fps since the Coral's processing slows down the counting
        # POSSIBLE alternative solution: first save the videos, nightly - process them.
        self.video_writer = VideoWriter(output_path='/home/mendel/mnt/resources/videos',
                                        fps=15.0)
        self.recording_last_face_seen_timestamp = 0

        self.face_detector = FaceDetector(model_path='/home/mendel/mnt/cameraSamples/examples-camera/all_models/mobilenet_ssd_v2_face_quant_postprocess_edgetpu.tflite')
        self.face_classifier = Classifier(using_model='/home/mendel/mnt/cameraSamples/examples-camera/imprinting_classification/retrained_imprinting_model.tflite',
                                          label_file='/home/mendel/mnt/cameraSamples/examples-camera/imprinting_classification/retrained_imprinting_model.txt')

        self.who = dict()
        self.counter = 0
        self.counter_up_down = False  # on off switch. False for human not visible (thus-down). True for face up.
        self.counting_prev_face_seen_timestamp = 0

    def _record(self, image, face_rois_in_image: List[List[int]]) -> Tuple[CONSTANTS.RECORD_STATUS, Union[None, str]]:
        seeing_a_face = len(face_rois_in_image) > 0

        if self.video_writer.is_video_recording_in_progress():
            # print("{}".format(time.time() - self.t0))  # timer used for debugging the video's fps
            # self.t0 = time.time()  # timer used for debugging the video's fps
            self.video_writer.add_image(numpy.array(image))

            if time.time() - self.recording_last_face_seen_timestamp >= CONSTANTS.NO_FACE_THRESHOLD_SEC:
                video_path = self.video_writer.video_name  # create a backup since stop_video_recording messes this up
                self.video_writer.stop_video_recording()
                self.recording_last_face_seen_timestamp = 0
                return CONSTANTS.RECORD_STATUS.JUST_STOPPED, video_path

            if seeing_a_face:
                self.recording_last_face_seen_timestamp = time.time()
                self.video_writer.save_image_at_same_path(numpy.array(image.crop(face_rois_in_image[0])))

            return CONSTANTS.RECORD_STATUS.ON, self.video_writer.video_name

        elif seeing_a_face:
            self.recording_last_face_seen_timestamp = time.time()
            self.video_writer.start_video_recording(numpy.array(image))
            self.video_writer.save_image_at_same_path(numpy.array(image.crop(face_rois_in_image[0])))
            return CONSTANTS.RECORD_STATUS.JUST_STARTED, self.video_writer.video_name

        return CONSTANTS.RECORD_STATUS.OFF, None

    def _count(self, face_rois_in_image: List[List[int]]) -> int:
        seeing_a_face = len(face_rois_in_image) > 0

        # if seeing a face and was not seeing a face before
        if seeing_a_face and not self.counter_up_down:
            self.counter_up_down = True  # up

            # if at least MIN_SEC_PER_PULLUP have passed, it means there was a pullup done
            # and the coral camera did not just lose focus
            if time.time() - self.counting_prev_face_seen_timestamp >= CONSTANTS.MIN_SEC_PER_PULLUP:
                self.counting_prev_face_seen_timestamp = time.time()
                self.counter += 1

        elif not seeing_a_face:
            self.counter_up_down = False  # down

        return self.counter

    def _whothis(self, image_of_face: Image) -> str:
        who_prediction = self.face_classifier.classify(image=image_of_face, top_k=len(self.face_classifier.labels))
        who_prediction = {str(k): v for k, v in who_prediction}
        for k in who_prediction:
            self.who[k] = self.who.get(k, 0.0) + who_prediction[k]
        maxid = max(self.who.items(), key=operator.itemgetter(1))[0]
        # print('who_now', who_prediction)
        # print('who_all', self.who)
        # print('who idx: ', maxid, int(maxid))
        # print('labels:  ', self.face_classifier.labels)

    def _write_number_on_photo(self, image: Image, number: int):
        ImageDraw.Draw(image).text((10, 8),
                                   text=str(number),
                                   fill=(255, 0, 0),
                                   font=ImageFont.truetype(font=CONSTANTS.font_path, size=24))

    def _save(self, who: str, pullup_counts: int, evidence_path: str):
        with open(CONSTANTS.db_path, "a+") as track_file:
            # when,who,how_many,evidence
            track_file.write('{},{},{},{}\n'.format(time.time(), who, pullup_counts, evidence_path))

    def _reset_session(self):
        self.counter = 0
        self.who = dict()

    def _callback(self, image, svg_canvas):
        face_rois_in_image = self.face_detector.predict(image)

        counts = self._count(face_rois_in_image=face_rois_in_image)
        self._write_number_on_photo(image, number=counts)

        record_status, video_path = self._record(image=image,
                                                 face_rois_in_image=face_rois_in_image)

        if len(face_rois_in_image) > 0:
            self._whothis(image_of_face=image.crop(face_rois_in_image[0]))

        if record_status == CONSTANTS.RECORD_STATUS.JUST_STOPPED:
            self._save(who=self.face_classifier.labels[int(max(self.who.items(), key=operator.itemgetter(1))[0])],
                       pullup_counts=self.counter,
                       evidence_path=video_path)
            self._reset_session()


    def sigint_handler(self, signum, frame):
        self.video_writer.stop_video_recording()

    def start(self):
        _ = gstreamer.run_pipeline(self._callback, appsink_size=(320, 240))
        self.video_writer.stop_video_recording()


def main():
    mainObject = Main()
    mainObject.start()

if __name__ == '__main__':
    main()
