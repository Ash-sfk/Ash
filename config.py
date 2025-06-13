"""
ZERIL Bot Configuration File
Created by @ash_yv
"""

import os
from typing import Dict, List

class ZerilConfig:
    # Bot Identity
    BOT_NAME = "ZERIL"
    CREATOR_USERNAME = "ash_yv"
    VERSION = "1.0.0"
    
    # API Tokens (from environment variables)
    BOT_TOKEN = os.getenv("BOT_TOKEN", "8092570026:AAHB4aPVGF4frTsm3SXPk_Xv3mLIcg6KHYM")
    HF_TOKEN = os.getenv("HF_TOKEN", "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")
    
    # AI Models Configuration
    MODELS = {
        "emotion": "bhadresh-savani/distilbert-base-uncased-emotion",
        "language": "papluca/xlm-roberta-base-language-detection", 
        "image_generation": "run
