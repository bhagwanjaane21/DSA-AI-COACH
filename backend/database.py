"""
Supabase client setup.
Provides a singleton Supabase client instance used across the application.
"""
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

_supabase_client: Client | None = None


def get_supabase() -> Client:
    """Get or create the Supabase client singleton."""
    global _supabase_client
    if _supabase_client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY must be set in .env file. "
                "Get these from your Supabase project dashboard."
            )
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client
