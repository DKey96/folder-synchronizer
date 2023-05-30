import datetime
import hashlib
import logging
import os
import shutil
import sys
import time


def get_logger(log_path):
    if not os.path.exists("./logs"):
        os.makedirs("./logs")
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
    logger = logging.getLogger(__name__)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    logger.addHandler(logging.FileHandler(f"{log_path}/sync_{timestamp}.log"))
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logger.addHandler(console)
    return logger


class SyncHandler:
    def __init__(self, src_folder: str, replica_folder: str, logger: logging.Logger) -> None:
        self.src_folder = src_folder
        self.replica_folder = replica_folder
        self.logger = logger

    @staticmethod
    def get_file_checksum(file_path: str) -> str:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as file:
            for chunk in iter(lambda: file.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def synchronize_folders(self) -> None:
        for root, dirs, files in os.walk(self.src_folder):
            relative_path = os.path.relpath(root, self.src_folder)
            replica_dir = os.path.join(self.replica_folder, relative_path)
            os.makedirs(replica_dir, exist_ok=True)

            for file in files:
                src_file = os.path.join(root, file)
                replica_file = os.path.join(replica_dir, file)

                src_checksum = self.get_file_checksum(src_file)
                replica_checksum = self.get_file_checksum(replica_file) if os.path.exists(replica_file) else ""

                if src_checksum != replica_checksum:
                    shutil.copy2(src_file, replica_file)
                    self.logger.info(f"File copied: {replica_file}")

        for root, dirs, files in os.walk(self.replica_folder, topdown=False):
            relative_path = os.path.relpath(root, self.replica_folder)
            src_dir = os.path.join(self.src_folder, relative_path)
            replica_dir = os.path.join(self.replica_folder, relative_path)

            for directory in dirs:
                src_subdir = os.path.join(src_dir, directory)
                replica_subdir = os.path.join(replica_dir, directory)
                if not os.path.exists(src_subdir):
                    shutil.rmtree(replica_subdir)
                    self.logger.info(f"Directory removed: {replica_subdir}")

            for file in files:
                replica_file = os.path.join(replica_dir, file)
                src_file = os.path.join(src_dir, file)
                if not os.path.exists(src_file):
                    os.remove(replica_file)
                    self.logger.info(f"File removed: {replica_file}")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python sync.py <source_folder> <replica_folder> <interval [seconds]> <logs_folder>")
        sys.exit(1)

    src = sys.argv[1]
    replica = sys.argv[2]
    log = sys.argv[4]

    if not os.path.exists(log):
        print(f"Log path `{log}` does not exists. Please insert a valid directory path.")
        sys.exit(1)

    logger = get_logger(log)

    try:
        interval = int(sys.argv[3])
    except ValueError:
        logger.error(f"Invalid interval `{sys.argv[3]}`. Interval should be an integer.")
        sys.exit(1)

    if not os.path.exists(src):
        logger.error(
            f"Source path `{src}` does not exists. Cannot sync non-existing folder. "
            f"Please insert a valid directory path.")
        sys.exit(1)
    if not os.path.exists(replica):
        logger.error(
            f"Replica path `{replica}` does not exists. Cannot sync non-existing folder. "
            f"Please insert a valid directory path.")
        sys.exit(1)
    if src == replica:
        logger.error(f"Source path cannot be the same as replica path.")
        sys.exit(1)
    if interval <= 0:
        logger.error(f"Invalid interval: `{interval}`. Interval must be positive number.")
        sys.exit(1)

    sync_handler = SyncHandler(src, replica, logger)
    logger.info(f"Syncing `{src}` to `{replica}` every `{interval}` seconds...")

    try:
        while True:
            sync_handler.synchronize_folders()
            time.sleep(interval)
    except KeyboardInterrupt:
        pass
