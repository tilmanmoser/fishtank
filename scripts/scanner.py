import os
import cv2
from cv2.typing import MatLike
import imutils
import numpy as np


class Scanner:

    def __init__(self) -> None:
        self.size = [600, 848]
        self.corners = np.float32([(0, 0), (self.size[0], 0), (self.size[0], self.size[1]), (0, self.size[1])])
        self.masks = self.load_masks()
        self.aruco_detector = cv2.aruco.ArucoDetector(
            dictionary=cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        )

    def load_masks(self):
        masks = []
        path = os.path.join("./data/images/fishes/mask")
        files = sorted([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.endswith(".png")])
        for file in files:
            masks.append(self.load_mask(path, file))
        return masks

    def load_mask(self, path, file):
        # load mask as is (with transparent background)
        mask = cv2.imread(os.path.join(path, file), 0)
        # since we crop images at the outer corners of aruco markers, we need to crop the mask the same way
        # in my case I set the aruco markers 100px away from each side (e.g. top left = 100,100)
        height, width = mask.shape
        translate_src = np.float32([(100, 100), (width - 100, 100), (width - 100, height - 100), (100, height - 100)])
        matrix = cv2.getPerspectiveTransform(translate_src, self.corners)
        mask = cv2.warpPerspective(mask, matrix, self.size)
        return mask

    def scan(self, file) -> tuple[MatLike | None, int | None]:
        # read and resize image
        image = cv2.imread(os.path.join(file))
        image = imutils.resize(image, width=self.size[0])

        # detect aruco markers
        (markers, ids, rejected) = self.aruco_detector.detectMarkers(image)

        translate_src = []
        translate_dst = []
        template_id = None

        for marker, id in zip(markers, ids.flatten()):
            # extract the marker corners (which are returned in top-left, top-right, bottom-right, and bottom-left order)
            corners = marker.reshape((4, 2))
            (topLeft, topRight, bottomRight, bottomLeft) = corners

            # extract translation points
            match id:
                case 0:
                    translate_src.append((int(topLeft[0]), int(topLeft[1])))
                    translate_dst.append(self.corners[0])
                case 1:
                    translate_src.append((int(topRight[0]), int(topRight[1])))
                    translate_dst.append(self.corners[1])
                case 2:
                    translate_src.append((int(bottomRight[0]), int(bottomRight[1])))
                    translate_dst.append(self.corners[2])
                case 3:
                    translate_src.append((int(bottomLeft[0]), int(bottomLeft[1])))
                    translate_dst.append(self.corners[3])
                case _:
                    template_id = id - 4

        if len(translate_src) != 4:
            return None, None

        # align image
        matrix = cv2.getPerspectiveTransform(np.float32(translate_src), np.float32(translate_dst))
        aligned = cv2.warpPerspective(image, matrix, self.size, flags=cv2.INTER_LINEAR)

        # if we recognized a template id and have a mask for it
        if template_id is not None and template_id < len(self.masks):
            # cutout a silhouette
            mask = self.masks[template_id]
            aligned = cv2.bitwise_and(aligned, aligned, mask=mask)

            # set alpha channel for transparent background
            alpha = np.sum(aligned, axis=-1) > 0
            alpha = np.uint8(alpha * 255)
            aligned = np.dstack((aligned, alpha))

        return aligned, template_id
