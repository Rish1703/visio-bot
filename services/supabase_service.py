from core.config import supabase, FREE_LIMIT

async def get_user_usage(user_id):
    data = supabase.table("usage").select("*").eq("user_id", user_id).execute().data
    if data:
        return data[0]
    else:
        supabase.table("usage").insert({
            "user_id": user_id,
            "count": 0,
            "limit": FREE_LIMIT
        }).execute()
        return {"user_id": user_id, "count": 0, "limit": FREE_LIMIT}

async def update_user_usage(user_id, count=None, limit=None):
    updates = {}
    if count is not None:
        updates["count"] = count
    if limit is not None:
        updates["limit"] = limit
    supabase.table("usage").update(updates).eq("user_id", user_id).execute()
