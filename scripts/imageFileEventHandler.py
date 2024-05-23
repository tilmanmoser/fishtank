import cv2
import os
from datetime import datetime
from watchdog.events import FileSystemEvent, FileSystemEventHandler


class ImageFileEventHandler(FileSystemEventHandler):
    def __init__(self, scanner, outbound, remove=False, callback=None):
        super().__init__()
        self.scanner = scanner
        self.remove = remove
        self.outbound = outbound
        self.callback = callback

    def on_created(self, event: FileSystemEvent) -> None:
        try:
            filename = self.scanner.scan(event.src_path)
            if filename is not None:
                if self.remove:
                    os.remove(event.src_path)
                if self.callback:
                    self.callback(filename)
            else:
                print(f"Failed to scan {event.src_path}")
        except Exception as error:
            print(error)
        return super().on_created(event)
