###############################################################################
# Wrapper module for musetalk real model
###############################################################################
from .real_impl import MuseReal, load_model, load_avatar, warm_up

__all__ = ["MuseReal", "load_model", "load_avatar", "warm_up"]
