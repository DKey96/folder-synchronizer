import os
import tempfile
import threading
import time
import unittest
from unittest.mock import MagicMock

from sync import SyncHandler


class SyncHandlerTests(unittest.TestCase):
    def test_file_copy(self):
        with tempfile.TemporaryDirectory() as src_folder, tempfile.TemporaryDirectory() as replica_folder:
            sync_handler = SyncHandler(src_folder, replica_folder, logger=MagicMock())
            with tempfile.NamedTemporaryFile(dir=src_folder) as src_file:
                src_file.write(b"Test")
                src_file.flush()
                sync_handler.synchronize_folders()
                replica_file = os.path.join(replica_folder, os.path.basename(src_file.name))
                self.assertTrue(os.path.exists(replica_file))
                with open(replica_file, 'rb') as f:
                    self.assertEqual(b"Test", f.read())

    def test_file_removal(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            src_folder = os.path.join(temp_dir, "src_folder")
            replica_folder = os.path.join(temp_dir, "replica_folder")
            os.makedirs(src_folder)
            os.makedirs(replica_folder)

            sync_handler = SyncHandler(src_folder, replica_folder, logger=MagicMock())

            src_file_path = os.path.join(src_folder, "test_file.txt")
            with open(src_file_path, "w") as src_file:
                src_file.write("Test")

            sync_handler.synchronize_folders()
            self.assertTrue(os.path.exists(src_file_path))

            replica_file_path = os.path.join(replica_folder, "test_file.txt")
            self.assertTrue(os.path.exists(replica_file_path))

            os.remove(src_file_path)
            sync_handler.synchronize_folders()
            self.assertFalse(os.path.exists(replica_file_path))

    def test_content_change(self):
        with tempfile.TemporaryDirectory() as src_folder, tempfile.TemporaryDirectory() as replica_folder:
            sync_handler = SyncHandler(src_folder, replica_folder, logger=MagicMock())
            with tempfile.NamedTemporaryFile(dir=src_folder) as src_file:
                src_file.write(b"Test")
                src_file.flush()

                src_file_basename = os.path.basename(src_file.name)
                replica_file_path = os.path.join(replica_folder, src_file_basename)
                os.makedirs(os.path.dirname(replica_file_path), exist_ok=True)
                with open(replica_file_path, 'wb') as replica_file:
                    replica_file.write(b"Different content")

                sync_handler.synchronize_folders()

                self.assertTrue(os.path.exists(replica_file_path))
                with open(replica_file_path, 'rb') as f:
                    self.assertEqual(b"Test", f.read())

    def test_interval(self):
        interval = 1
        with tempfile.TemporaryDirectory() as src_folder, tempfile.TemporaryDirectory() as replica_folder:
            sync_handler = SyncHandler(src_folder, replica_folder, logger=MagicMock())
            with tempfile.NamedTemporaryFile(dir=src_folder) as src_file:
                src_file.write(b"Test")
                src_file.flush()

                sync_thread = threading.Thread(target=sync_handler.synchronize_folders)
                sync_thread.start()

                time.sleep(interval)
                replica_file = os.path.join(replica_folder, os.path.basename(src_file.name))
                self.assertTrue(os.path.exists(replica_file))

                sync_thread.join()
