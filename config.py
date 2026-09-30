import os

from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# GEMINI API
# ============================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    "",
)


# Gemini 3.1 Flash Lite
# Free-tier limits shown in your Google AI Studio:
# RPM: 15
# TPM: 250K
# RPD: 500
GEMINI_MODEL = "gemini-3.1-flash-lite"


# ============================================================
# LOCAL EXPLANATION
# ============================================================

ENABLE_LOCAL_EXPLANATION = os.getenv(
    "ENABLE_LOCAL_EXPLANATION",
    "false",
).lower() == "true"


LOCAL_EXPLANATION_MODEL = os.getenv(
    "LOCAL_EXPLANATION_MODEL",
    "MBZUAI/LaMini-Flan-T5-783M",
)


# ============================================================
# GENERATION SETTINGS
# ============================================================

# Keep responses reasonably short to reduce token usage.
MAX_OUTPUT_TOKENS = int(
    os.getenv(
        "MAX_OUTPUT_TOKENS",
        "1200",
    )
)


# Lower temperature gives more consistent educational answers.
TEMPERATURE = float(
    os.getenv(
        "TEMPERATURE",
        "0.3",
    )
)