import os
from pathlib import Path
import cv2


def generate_aruco_markers(dictionary_type=cv2.aruco.DICT_4X4_50, amount=16, size=200):
    dictionary = cv2.aruco.getPredefinedDictionary(dictionary_type)
    markers = []
    for i in range(amount):
        marker = cv2.aruco.generateImageMarker(dictionary=dictionary, id=i, sidePixels=size)
        markers.append(marker)
    return markers


def main():
    Path(os.path.join("./data/aruco")).mkdir(parents=True, exist_ok=True)
    markers = generate_aruco_markers()
    for i, marker in enumerate(markers):
        cv2.imwrite(os.path.join("./data/aruco", f"aurco-{i}.png"), marker)


if __name__ == "__main__":
    main()
