# Compatibility shim for chromadb with pydantic v2
# This must run before any chromadb imports
import sys

# Patch pydantic's __getattr__ to return BaseSettings from pydantic_settings
def _patch_pydantic():
    try:
        import pydantic
        from pydantic_settings import BaseSettings
        
        # Add BaseSettings as direct attribute first
        pydantic.BaseSettings = BaseSettings
        
        # Store original __getattr__ if it exists
        if hasattr(pydantic, '__getattr__'):
            original_getattr = pydantic.__getattr__
        else:
            original_getattr = None
        
        def patched_getattr(name):
            if name == "BaseSettings":
                return BaseSettings
            # Fall back to original __getattr__ for other attributes
            if original_getattr:
                return original_getattr(name)
            raise AttributeError(f"module 'pydantic' has no attribute '{name}'")
        
        # Replace __getattr__ with patched version
        pydantic.__getattr__ = patched_getattr
    except (ImportError, AttributeError) as e:
        # If patching fails, continue - error will show when chromadb is used
        pass

# Patch ChromaDB Settings to ignore extra fields from .env file
# This patches pydantic-settings to filter out non-ChromaDB env vars for ChromaDB
def _patch_chromadb_settings():
    try:
        # Patch pydantic_settings to not read .env file for ChromaDB
        # We do this by temporarily modifying how Settings reads env vars
        import pydantic_settings
        from pydantic_settings import BaseSettings
        
        # Store original _build_values if it exists
        original_build_values = getattr(BaseSettings, "_settings_build_values", None)
        
        if original_build_values:
            def patched_build_values(cls, values, init_settings, env_settings, dotenv_settings, file_secret_settings):
                # For ChromaDB Settings, filter out app-specific env vars
                if "chromadb" in cls.__module__.lower() or "Settings" in cls.__name__:
                    # Filter environment to only include ChromaDB-specific vars
                    import os
                    chroma_prefixes = ["CHROMA_", "CLICKHOUSE_"]
                    filtered_env = {
                        k: v for k, v in os.environ.items()
                        if any(k.startswith(prefix) for prefix in chroma_prefixes)
                    }
                    # Temporarily replace os.environ
                    original_env = os.environ.copy()
                    os.environ.clear()
                    os.environ.update(filtered_env)
                    try:
                        result = original_build_values(values, init_settings, env_settings, dotenv_settings, file_secret_settings)
                    finally:
                        os.environ.clear()
                        os.environ.update(original_env)
                    return result
                return original_build_values(values, init_settings, env_settings, dotenv_settings, file_secret_settings)
            
            # This approach is too complex and risky. Let's use a simpler method.
            # Instead, we'll patch the Settings class after chromadb imports it.
    except (ImportError, AttributeError, Exception):
        pass

# Apply pydantic patch
_patch_pydantic()

