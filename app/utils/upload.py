from supabase import create_client

from app.utils import env


supabase = create_client(
    env.SUPABASE_URL,
    env.SUPABASE_SERVICE_KEY
)

def upload(filename:str, content: bytes, content_type: str):
    supabase.storage.from_("profile_images")\
    .upload(
        path=filename,
        file=content,
        file_options={
            "content-type": content_type,
            "upsert": "true",
        }
    )

    url = (
        supabase.storage.from_("profile_images")
        .get_public_url(filename)
    )

    return url