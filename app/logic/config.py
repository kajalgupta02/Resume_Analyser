"""Loading and validation of analysis configuration."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

DEFAULT_CONFIG_PATH = Path(__file__).with_name("analysis_config.json")


@lru_cache(maxsize=4)
def load_analysis_config(config_path: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    path = Path(config_path or DEFAULT_CONFIG_PATH).expanduser().resolve()
    with path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    if not isinstance(config, dict):
        raise ValueError("Analysis config must be a JSON object")
    return config
