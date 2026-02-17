from typing import Protocol


class FileSystem(Protocol):
    def ls(self, path: str) -> list[str]: ...

    def glob(self, path: str) -> list[str]: ...

    def is_dir(self, path: str) -> bool: ...

    def join(self, *parts: str) -> str: ...


class LocalFileSystem:
    def ls(self, path: str) -> list[str]:
        import os

        return [os.path.join(path, entry) for entry in os.listdir(path)]

    def glob(self, path: str) -> list[str]:
        import glob

        return glob.glob(path)

    def is_dir(self, path: str) -> bool:
        import os

        return os.path.isdir(path)

    def join(self, *parts: str) -> str:
        import os

        return os.path.join(*parts)


class S3FileSystem:
    def __init__(self):
        import s3fs

        self.s3 = s3fs.S3FileSystem()

    def ls(self, path: str) -> list[str]:
        return self.s3.ls(path)

    def glob(self, path: str) -> list[str]:
        return self.s3.glob(path)

    def is_dir(self, path: str) -> bool:
        return self.s3.isdir(path)

    def join(self, *parts: str) -> str:
        return "/".join(p.strip("/") for p in parts if p)
