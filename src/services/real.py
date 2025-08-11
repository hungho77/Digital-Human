###############################################################################
# Real service wrapper
#
# Provides a unified API to load/cache model assets (weights, avatar data)
# and build the corresponding Real implementation (musetalk / wav2lip / ultralight).
#
# Usage:
#   model, avatar = ensure_model_loaded(opt)
#   real = build_real(opt, model, avatar)
#
# This mirrors the style of src/services/tts.py (service wrapper approach).
###############################################################################
from __future__ import annotations

from typing import Dict, Tuple, Any
from threading import Lock

from src.utils.logger import logger

# Import Real classes and their loaders
# MuseTalk
from src.models.musetalk.real import (
    MuseReal as _MuseReal,
    load_model as _muse_load_model,
    load_avatar as _muse_load_avatar,
    warm_up as _muse_warm_up,
)

# Wav2Lip
from src.models.wav2lip.real import (
    LipReal as _Wav2LipReal,
    load_model as _wav_load_model,
    load_avatar as _wav_load_avatar,
    warm_up as _wav_warm_up,
)

# Ultralight
from src.models.ultralight.real import (
    LightReal as _UltraLightReal,
    load_model as _ultra_load_model,
    load_avatar as _ultra_load_avatar,
    warm_up as _ultra_warm_up,
)


# Registry describing how to load and build each real type
_REAL_REGISTRY = {
    "musetalk": {
        "class": _MuseReal,
        "load_model": _muse_load_model,
        "load_avatar": _muse_load_avatar,
        "warm_up": _muse_warm_up,
    },
    "wav2lip": {
        "class": _Wav2LipReal,
        "load_model": _wav_load_model,
        "load_avatar": _wav_load_avatar,
        "warm_up": _wav_warm_up,
    },
    "ultralight": {
        "class": _UltraLightReal,
        "load_model": _ultra_load_model,
        "load_avatar": _ultra_load_avatar,
        "warm_up": _ultra_warm_up,
    },
}


# Cache: (model_name, avatar_id) -> (model, avatar)
_MODEL_CACHE: Dict[Tuple[str, str], Tuple[Any, Any]] = {}
_CACHE_LOCK = Lock()


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
        raise ValueError("opt.model and opt.avatar_id must be set before loading model")

    key = (model_name, avatar_id)
    with _CACHE_LOCK:
        if key in _MODEL_CACHE:
            return _MODEL_CACHE[key]

        if model_name not in _REAL_REGISTRY:
            raise ValueError(f"Unknown model '{model_name}'. Expected one of: {list(_REAL_REGISTRY.keys())}")

        entry = _REAL_REGISTRY[model_name]
        logger.info("Loading model assets for %s (avatar=%s)", model_name, avatar_id)
        load_model_fn = entry["load_model"]
        load_avatar_fn = entry["load_avatar"]
        warm_up_fn = entry["warm_up"]

        # Load assets
        model = load_model_fn() if model_name == "musetalk" else load_model_fn(getattr(opt, "model_path", None) or opt)
        avatar = load_avatar_fn(avatar_id)

        # Warm up
        _do_warm_up(model_name, warm_up_fn, opt, model, avatar)

        _MODEL_CACHE[key] = (model, avatar)
        return _MODEL_CACHE[key]


def build_real(opt, model=None, avatar=None):
    """Instantiate the Real implementation for the selected model.

    - If model/avatar are not provided, they will be loaded/cached automatically.
    - Returns a concrete instance of BaseReal subclass (MuseReal/LipReal/LightReal).
    """
    model_name = getattr(opt, "model", None)
    if not model_name:
        raise ValueError("opt.model must be set (musetalk | wav2lip | ultralight)")

    if model is None or avatar is None:
        model, avatar = ensure_model_loaded(opt)

    entry = _REAL_REGISTRY.get(model_name)
    if entry is None:
        raise ValueError(f"Unknown model '{model_name}'. Expected one of: {list(_REAL_REGISTRY.keys())}")

    real_cls = entry["class"]
    logger.info("Building real instance: %s", real_cls.__name__)
    return real_cls(opt, model, avatar)


def clear_model_cache():
    """Clear all cached model assets."""
    with _CACHE_LOCK:
        _MODEL_CACHE.clear()


__all__ = [
    "ensure_model_loaded",
    "build_real",
    "clear_model_cache",
]


