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
            img, template_id = self.scanner.scan(event.src_path)
            if img is not None:
                date = datetime.now().strftime("%Y%m%d%H%M%S%f")
                file = os.path.join(self.outbound, f"{date}-{template_id}.png")
                cv2.imwrite(file, img)
                if self.remove:
                    os.remove(event.src_path)
                if self.callback:
                    self.callback(file)
            else:
                print(f"Failed to scan {event.src_path}")
        except Exception as error:
            print(error)
        return super().on_created(event)
