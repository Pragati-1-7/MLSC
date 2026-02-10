import os
from dotenv import load_dotenv

load_dotenv()

# Algorand Node Configuration (Default: LocalNet)
ALGOD_ADDRESS = os.getenv("ALGOD_ADDRESS", "http://localhost:4001")
ALGOD_TOKEN = os.getenv("ALGOD_TOKEN", "a" * 64)

# App ID of the Smart Contract
APP_ID = int(os.getenv("APP_ID", 0))

# Threshold for Absence Alert (40%)
ABSENCE_THRESHOLD = 0.40
