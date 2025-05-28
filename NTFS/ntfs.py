import os
import time

class VirtualNTFSDisk:
    def __init__(self, disk_path, size_bytes=1024*1024):
        self.disk_path = disk_path
        self.size_bytes = size_bytes
        if not os.path.exists(disk_path):
            os.makedirs(disk_path)

    def format(self):
        print(f"Initialized virtual disk of size {self.size_bytes} Bytes.")
        print("Formatting virtual disk with NTFS...")
        time.sleep(1)
        print("NTFS metadata written successfully.")
        print("Master File Table (MFT) initialized.")
        print("Virtual disk formatted with NTFS.")

    def create_file(self, filename, content):
        content_bytes = content.encode('utf-8')
        if len(content_bytes) > self.size_bytes:
            raise Exception("Not enough space on disk!")
        with open(os.path.join(self.disk_path, filename), 'w', encoding='utf-8') as f:
            f.write(content)

    def list_files(self):
        return os.listdir(self.disk_path)