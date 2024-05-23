import math
import os
import cv2
import numpy as np
import pygame
import time
from datetime import datetime


class Capture:

    def __init__(self, scanner, outbound, size=(320, 240), pos=(0, 0), callback=None) -> None:
        self.scanner = scanner
        self.outbound = outbound
        self.temp = os.path.join("data/temp")
        self.size = size
        self.pos = pos
        self.callback = callback

        self.capture = None
        self.last_frame_ts = 0
        self.frame = pygame.Surface(size)
        self.frame.fill((0, 0, 0))

        self.aruco_detector = cv2.aruco.ArucoDetector(
            dictionary=cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        )

        self.instructions = pygame.image.load(os.path.join("data/images/capture/instructions.png")).convert_alpha()
        self.closer = pygame.image.load(os.path.join("data/images/capture/closer.png")).convert_alpha()

    def open(self):
        try:
            self.capture = cv2.VideoCapture(0)
        except Exception:
            pass

    def close(self):
        try:
            self.capture.close()
        except Exception:
            pass
        finally:
            self.capture = None

    def isCapturing(self):
        return isinstance(self.capture, cv2.VideoCapture) and self.capture.isOpened()

    def update(self):
        if self.isCapturing() and time.time() - self.last_frame_ts > (1.0 / 25):
            success, frame = self.capture.read()
            if success:
                show_instructions = False
                show_come_closer = False

                # get frame dimensions
                height, width, channels = frame.shape
                diagonal = math.hypot(height, width)

                # convert to gray color
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # detect aruco markers
                (markers, ids, rejected) = self.aruco_detector.detectMarkers(gray)

                # if all expected markers are detected in frame
                if len(markers) == 5:
                    # calculate the centers of each marker
                    corners = []
                    for marker in markers:
                        marker = marker.reshape(4, 2)
                        corners.append(
                            (
                                marker[0][0] + (marker[2][0] - marker[0][0]) / 2,
                                marker[0][1] + (marker[2][1] - marker[0][1]) / 2,
                            )
                        )

                    # calculate the diagonal between min/max corner
                    corners = np.array(corners)[: np.newaxis]
                    corners_diagonal = math.hypot(
                        np.max(np.max(corners, 0)) - np.min(np.min(corners, 0)),
                        np.max(np.max(corners, 1)) - np.min(np.min(corners, 1)),
                    )

                    # if the drawing is close enough scan it
                    if (corners_diagonal / diagonal) > 0.75:
                        date = datetime.now().strftime("%Y%m%d%H%M%S%f")
                        temp_file = os.path.join(self.temp, f"{date}.png")
                        cv2.imwrite(temp_file, frame)
                        image_file = self.scanner.scan(temp_file)
                        if image_file is not None:
                            if self.callback:
                                self.callback(image_file)
                                self.close()
                    else:
                        show_come_closer = True
                else:
                    show_instructions = True

                # draw frame in pygame
                pg_frame = pygame.image.frombuffer(frame.tobytes(), frame.shape[1::-1], "BGR")
                scale = min(self.size[0] / pg_frame.get_width(), self.size[1] / pg_frame.get_height())
                self.frame = pygame.transform.scale_by(pg_frame, scale)
                if show_instructions:

                    self.frame.blit(pygame.transform.scale(self.instructions, self.frame.get_size()), (0, 0))
                elif show_come_closer:
                    self.frame.blit(pygame.transform.scale(self.closer, self.frame.get_size()), (0, 0))

                self.last_frame_ts = time.time()

            else:
                # show black screen if we've got no image from camera
                self.frame = pygame.Surface(self.size)
                self.frame.fill((0, 0, 0, 0))

    def render(self, surface):
        if self.frame:
            surface.blit(self.frame, self.pos)
