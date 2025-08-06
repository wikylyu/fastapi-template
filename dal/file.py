from dal.base import BaseRepo
from models.file import File


class FileRepo(BaseRepo):
    async def create_file(
        self, filename: str = "", content_type: str = "", size: int = 0, admin_user_id: int = 0
    ) -> File:
        file = File(filename=filename, content_type=content_type, size=size, admin_user_id=admin_user_id)
        self.db.add(file)
        await self.db.flush()
        return file

    async def get_file(self, id: str) -> File | None:
        return await self.db.get(File, id)
