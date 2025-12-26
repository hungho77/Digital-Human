"""Avatar model implementations (MuseTalk, Wav2Lip, Ultralight, etc.)."""

from src.services.avatar_models.model_manager import (
    load_avatar_processor,
    ensure_model_loaded,
    clear_model_cache,
)

__all__ = ["load_avatar_processor", "ensure_model_loaded", "clear_model_cache"]
