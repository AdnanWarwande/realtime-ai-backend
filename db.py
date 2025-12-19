from supabase import create_client
from config import get_settings
import asyncio
from datetime import datetime, timezone

settings = get_settings()
supabase = create_client(settings.supabase_url, settings.supabase_key)

async def create_session(user_id):
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: supabase.table('sessions').insert({
            'user_id': user_id,
            'status': 'active'
        }).execute()
    )
    return response.data[0]['session_id']

async def log_event(session_id, event_type, content, metadata=None):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        lambda: supabase.table('event_log').insert({
            'session_id': str(session_id),
            'event_type': event_type,
            'content': content,
            'metadata': metadata or {}
        }).execute()
    )

async def get_session_history(session_id):
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: supabase.table('event_log').select('*').eq('session_id', str(session_id)).order('timestamp').execute()
    )
    return response.data

async def update_session_summary(session_id, summary, duration):
    loop = asyncio.get_event_loop()
    update_data = {
        'end_time': datetime.now(timezone.utc).isoformat(),
        'duration_seconds': duration,
        'summary': summary,
        'status': 'completed'
    }
    await loop.run_in_executor(
        None,
        lambda: supabase.table('sessions').update(update_data).eq('session_id', str(session_id)).execute()
    )
