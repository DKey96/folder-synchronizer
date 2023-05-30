# Folder Synchronizer

Implementation of a program that synchronizes two folders: source and replica. 
The program should maintain a full, identical copy of source folder at replica folder.

The synchronization is done one-way (from source to replica).
Synchronization is done periodically based on the interval specified by the user.

## Requirements
- Python >= 3.7

## How to use
- Call the command above with specified attributes:
```bash
python3 sync.py <SOURCE_PATH> <REPLICA_PATH> <INTERVAL> <LOGS_FOLDER_PATH>
```
- SOURCE_PATH and REPLICA_PATH shall be strings pointing to the path of the folders.
- INTERVAL shall be and positive integer higher than 0. 
- LOGS_FOLDER_PATH shall be a path to the directory, where logs may be stored