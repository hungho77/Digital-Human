"""Avatar model management and caching (refactored from services/real.py)."""

from typing import Tuple, Any
from threading import Lock
from src.processors.avatar.base_avatar import BaseAvatarProcessor
from src.utils.logger import logger

_MODEL_CACHE = {}
_CACHE_LOCK = Lock()


def _import_model_modules(model_name: str):
    """Dynamically import model modules to avoid dependency issues."""
    if model_name == "wav2lip":
        from src.modules.wav2lip.real import LipReal, load_avatar, load_model, warm_up

        return LipReal, load_model, load_avatar, warm_up
    elif model_name == "ultralight":
        from src.modules.ultralight.real import (
            LightReal,
            load_avatar,
            load_model,
            warm_up,
        )

        return LightReal, load_model, load_avatar, warm_up
    elif model_name == "musetalk":
        try:
            from src.modules.musetalk.real import (
                MuseReal,
                load_avatar,
                load_model,
                warm_up,
            )

            return MuseReal, load_model, load_avatar, warm_up
        except ImportError as e:
            logger.error(f"Failed to import musetalk: {e}")
            logger.error(
                "MuseTalk requires additional dependencies like diffusers, transformers compatibility"
            )
            raise ImportError(
                f"MuseTalk model not available due to missing dependencies: {e}"
            )
    else:
        raise ValueError(
            f"Unknown model '{model_name}'. Expected: wav2lip, ultralight, or musetalk"
        )


def _do_warm_up(model_name: str, warm_up_fn, opt, model, avatar) -> None:
    """Call warm_up with the appropriate signature for each model family."""
    try:
        if model_name == "wav2lip":
            # Model resolution defaults to 256 in the original pipeline
            warm_up_fn(opt.batch_size, model, 256)
        elif model_name == "ultralight":
            # Avatar-dependent, defaults to 160 in the original pipeline
            warm_up_fn(opt.batch_size, avatar, 160)
        elif model_name == "musetalk":
            warm_up_fn(opt.batch_size, model)
        else:
            logger.warning("Unknown model '%s' for warm_up; skipping", model_name)
    except Exception as exc:
        logger.warning("warm_up failed for %s: %s", model_name, exc)


def ensure_model_loaded(opt) -> Tuple[Any, Any]:
    """Load (or fetch from cache) the model assets for opt.model and opt.avatar_id.

    Returns: (model, avatar)
    """
    model_name = getattr(opt, "model", None)
    avatar_id = getattr(opt, "avatar_id", None)
    if not model_name or not avatar_id:
        raise ValueError(
            "opt.model and opt.avatar_id must be set before loading model"
        )

    key = (model_name, avatar_id)
    with _CACHE_LOCK:
        if key in _MODEL_CACHE:
            return _MODEL_CACHE[key]

        logger.info("Loading model assets for %s (avatar=%s)", model_name, avatar_id)

        # Import modules dynamically
        real_cls, load_model_fn, load_avatar_fn, warm_up_fn = _import_model_modules(
            model_name
        )

        # Load assets
        if model_name == "musetalk":
            model = load_model_fn()
        elif model_name == "wav2lip":
            model_path = (
                getattr(opt, "model_path", None) or "./models/wav2lip/wav2lip.pth"
            )
            model = load_model_fn(model_path)
        else:  # ultralight
            model_path = (
                getattr(opt, "model_path", None)
                or "./models/ultralight/ultralight.pth"
            )
            model = load_model_fn(model_path)
        avatar = load_avatar_fn(avatar_id)

        # Warm up
        _do_warm_up(model_name, warm_up_fn, opt, model, avatar)

        _MODEL_CACHE[key] = (model, avatar)
        return _MODEL_CACHE[key]


def load_avatar_processor(opt) -> BaseAvatarProcessor:
    """
    Load avatar processor for the specified model.

    Args:
        opt: Configuration options (contains opt.model, opt.avatar_id)

    Returns:
        BaseAvatarProcessor instance (MuseReal, LipReal, LightReal wrapped as processor)
    """
    model_name = getattr(opt, "model", None)
    if not model_name:
        raise ValueError("opt.model must be set (musetalk | wav2lip | ultralight)")

    model, avatar = ensure_model_loaded(opt)

    # Import the class dynamically
    real_cls, _, _, _ = _import_model_modules(model_name)

    logger.info("Building avatar processor: %s", real_cls.__name__)
    return real_cls(opt, model, avatar)


def clear_model_cache():
    """Clear all cached model assets."""
    with _CACHE_LOCK:
        _MODEL_CACHE.clear()


__all__ = [
    "ensure_model_loaded",
    "load_avatar_processor",
    "clear_model_cache",
]
