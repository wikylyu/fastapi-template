import aioboto3

from config import S3_ACCESS_KEY, S3_BUCKET, S3_ENDPOINT, S3_REGION, S3_SECRET_KEY


class S3Service:
    def __init__(self, access_key: str, secret_key: str, bucket: str, endpoint: str, region: str):
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket = bucket
        self.endpoint = endpoint
        self.region = region

    async def upload(self, key: str, body: any, content_type: str = ""):
        async with aioboto3.Session().client(
            "s3",
            region_name=self.region,
            endpoint_url=f"https://{self.endpoint}",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        ) as s3_client:
            await s3_client.put_object(Body=body, Bucket=self.bucket, Key=key, ContentType=content_type)

    async def download(self, key: str) -> bytes:
        async with aioboto3.Session().client(
            "s3",
            region_name=self.region,
            endpoint_url=f"https://{self.endpoint}",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        ) as s3_client:
            r = await s3_client.get_object(Bucket=self.bucket, Key=key)
            content = bytearray()
            async for chunk in r["Body"]:
                content.extend(chunk)

            return bytes(content)


def get_s3_service() -> S3Service:
    return S3Service(S3_ACCESS_KEY, S3_SECRET_KEY, S3_BUCKET, S3_ENDPOINT, S3_REGION)
