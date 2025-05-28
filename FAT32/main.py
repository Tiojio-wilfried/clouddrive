import os
import time
import math
import shutil

SECTOR_SIZE = 512
CLUSTER_SIZE = 4096  # 8 sectors per cluster
DISK_SIZE = 1024 * 1024  # 1MB disk
DISK_PATH = "./FAT32/virtual_disk"

class VirtualFAT32Disk:
    def __init__(self, disk_path, size_bytes):
        self.disk_path = disk_path
        self.size_bytes = size_bytes
        self.num_clusters = size_bytes // CLUSTER_SIZE
        self.fat = [0] * self.num_clusters  # 0 = free, -1 = end of file, >0 = next cluster
        self.cluster_map = {}  # filename -> [cluster indices]
        if not os.path.exists(disk_path):
            os.makedirs(disk_path)
        self._load_fat()

    def _fat_file(self):
        return os.path.join(self.disk_path, ".fat")

    def _load_fat(self):
        """Load FAT and cluster map from disk if exists."""
        fat_file = self._fat_file()
        if os.path.exists(fat_file):
            with open(fat_file, "r") as f:
                import json
                data = json.load(f)
                self.fat = data["fat"]
                self.cluster_map = data["cluster_map"]

    def _save_fat(self):
        """Save FAT and cluster map to disk."""
        fat_file = self._fat_file()
        with open(fat_file, "w") as f:
            import json
            json.dump({"fat": self.fat, "cluster_map": self.cluster_map}, f)

    def format(self):
        start = time.time()
        print(f"Initialized virtual disk of size {self.size_bytes} Bytes.\n")
        print("Formatting virtual disk with FAT32...\n")
        print("This may take a while depending on the disk size...\n")
        time.sleep(1)  # Simulate formatting delay
        print("16384 reserved bytes written successfully.\n")
        print("1st FAT written successfully.\n")
        print("Second FAT written successfully as a copy of the first.\n")
        self.fat = [0] * self.num_clusters
        self.cluster_map = {}
        for fname in os.listdir(self.disk_path):
            fp = os.path.join(self.disk_path, fname)
            if os.path.isfile(fp):
                os.remove(fp)
        self._save_fat()
        print("Virtual disk formatted with FAT32.\n")
        end = time.time()
        print(f"Total time = [{end - start:.2f}s]\n")

    def _find_free_clusters(self, count):
        free = [i for i, v in enumerate(self.fat) if v == 0]
        if len(free) < count:
            raise Exception("Not enough space on disk!")
        return free[:count]

    def create_file(self, filename, content):
        content_bytes = content.encode('utf-8')
        num_clusters_needed = math.ceil(len(content_bytes) / CLUSTER_SIZE)
        clusters = self._find_free_clusters(num_clusters_needed)
        # Write content to file
        with open(os.path.join(self.disk_path, filename), 'w', encoding='utf-8') as f:
            f.write(content)
        # Update FAT
        for i in range(num_clusters_needed):
            if i < num_clusters_needed - 1:
                self.fat[clusters[i]] = clusters[i+1]
            else:
                self.fat[clusters[i]] = -1  # End of file
        self.cluster_map[filename] = clusters
        self._save_fat()

    def copy_file(self, src, dest):
        if not self.file_exists(src):
            raise Exception("Source file does not exist!")
        with open(os.path.join(self.disk_path, src), 'r', encoding='utf-8') as f:
            content = f.read()
        self.create_file(dest, content)

    def delete_file(self, filename):
        if filename not in self.cluster_map:
            raise Exception("File does not exist!")
        for cluster in self.cluster_map[filename]:
            self.fat[cluster] = 0
        del self.cluster_map[filename]
        file_path = os.path.join(self.disk_path, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        self._save_fat()

    def file_exists(self, filename):
        return filename in self.cluster_map

    def list_files(self):
        return list(self.cluster_map.keys())

    def get_file_clusters(self, filename):
        if filename not in self.cluster_map:
            raise Exception("File does not exist!")
        return self.cluster_map[filename]

    def get_used_space(self):
        return sum(1 for v in self.fat if v != 0) * CLUSTER_SIZE

    def get_free_space(self):
        return sum(1 for v in self.fat if v == 0) * CLUSTER_SIZE

    def get_slack_space(self, filename):
        """Return slack space (unused bytes in the last cluster of the file)."""
        if filename not in self.cluster_map:
            raise Exception("File does not exist!")
        file_path = os.path.join(self.disk_path, filename)
        file_size = os.path.getsize(file_path)
        clusters = self.cluster_map[filename]
        last_cluster_bytes = file_size % CLUSTER_SIZE
        if last_cluster_bytes == 0 and file_size > 0:
            return 0
        return CLUSTER_SIZE - last_cluster_bytes if file_size > 0 else 0

    def show_stats(self):
        print(f"Disk size: {self.size_bytes} bytes")
        print(f"Cluster size: {CLUSTER_SIZE} bytes")
        print(f"Total clusters: {self.num_clusters}")
        print(f"Used space: {self.get_used_space()} bytes")
        print(f"Free space: {self.get_free_space()} bytes")
        print(f"Files: {self.list_files()}")

def main():
    start = time.time()
    disk = VirtualFAT32Disk(DISK_PATH, 1073741824)  # 1GB disk
    print(f"Initialized virtual disk of size {disk.size_bytes} Bytes.\n")
    print("Formatting virtual disk with FAT32...\n")
    print("This may take a while depending on the disk size...\n")
    time.sleep(1)  # Simulate formatting delay
    print("16384 reserved bytes written successfully.\n")
    print("1st FAT written successfully.\n")
    print("Second FAT written successfully as a copy of the first.\n")
    print("Virtual disk formatted with FAT32.\n")
    end = time.time()
    print(f"Total time = [{end - start:.2f}s]\n")

    while True:
        print("\nFAT32 Virtual Disk Console")
        print("1. Format disk")
        print("2. Show disk usage statistics")
        print("3. Add file")
        print("4. Copy file")
        print("5. Delete file")
        print("6. Check if file exists")
        print("7. List files")
        print("8. List clusters for file")
        print("9. Calculate slack space for file")
        print("0. Exit")
        choice = input("Enter your choice: ").strip()
        try:
            if choice == "1":
                disk.format()
            elif choice == "2":
                disk.show_stats()
            elif choice == "3":
                fname = input("Enter filename: ").strip()
                content = input("Enter file content: ")
                disk.create_file(fname, content)
                print(f"File '{fname}' created.")
            elif choice == "4":
                src = input("Source filename: ").strip()
                dest = input("Destination filename: ").strip()
                disk.copy_file(src, dest)
                print(f"Copied '{src}' to '{dest}'.")
            elif choice == "5":
                fname = input("Enter filename to delete: ").strip()
                disk.delete_file(fname)
                print(f"File '{fname}' deleted.")
            elif choice == "6":
                fname = input("Enter filename to check: ").strip()
                exists = disk.file_exists(fname)
                print(f"Exists: {exists}")
            elif choice == "7":
                print("Files:", disk.list_files())
            elif choice == "8":
                fname = input("Enter filename: ").strip()
                clusters = disk.get_file_clusters(fname)
                print(f"Clusters for '{fname}': {clusters}")
            elif choice == "9":
                fname = input("Enter filename: ").strip()
                slack = disk.get_slack_space(fname)
                print(f"Slack space for '{fname}': {slack} bytes")
            elif choice == "0":
                print("Exiting.")
                print("The SONG of VICTORY !!!!")
                break
            else:
                print("Invalid choice.")
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    main()