from fastapi import APIRouter, Depends, UploadFile
from fastapi import File as UFile

from dal.file import FileRepo
from middlewares.depends import get_current_admin_user
from models.admin import AdminUser
from routers.adminapi.schemas.file import FileSchema
from routers.response import R
from services.s3 import S3Service, get_s3_service

router = APIRouter()


@router.post("/", response_model=R[FileSchema], summary="上传文件", description="上传文件")
async def upload(
    upload_file: UploadFile = UFile(alias="file"),
    file_repo: FileRepo = Depends(FileRepo.get),
    cuser: AdminUser = Depends(get_current_admin_user),
    s3_service: S3Service = Depends(get_s3_service),
):
    content_type = upload_file.content_type
    content = await upload_file.read()

    file = await file_repo.create_file(upload_file.filename, content_type, upload_file.size, admin_user_id=cuser.id)

    await s3_service.upload(file.id, body=content, content_type=content_type)

    return R.success(file)
