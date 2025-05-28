from ntfs import VirtualNTFSDisk
import os

def main():
    disk = VirtualNTFSDisk("./NTFS/virtual_disk", size_bytes=1024*1024)
    disk.format()
    print("Welcome to the NTFS Virtual Disk CLI!")
    while True:
        print("\nOptions:")
        print("1. Create file")
        print("2. List files")
        print("3. Read file")
        print("4. Delete file")
        print("5. Exit")
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            filename = input("Enter filename: ").strip()
            content = input("Enter file content: ")
            try:
                disk.create_file(filename, content)
                print(f"File '{filename}' created.")
            except Exception as e:
                print(e)
        elif choice == "2":
            print("Files:", disk.list_files())
        elif choice == "3":
            filename = input("Enter filename to read: ").strip()
            try:
                with open(os.path.join("./NTFS/virtual_disk", filename), "r", encoding="utf-8") as f:
                    print("Content:", f.read())
            except Exception as e:
                print(e)
        elif choice == "4":
            filename = input("Enter filename to delete: ").strip()
            try:
                os.remove(os.path.join("./NTFS/virtual_disk", filename))
                print(f"File '{filename}' deleted.")
            except Exception as e:
                print(e)
        elif choice == "5":
            print("Exiting. Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()