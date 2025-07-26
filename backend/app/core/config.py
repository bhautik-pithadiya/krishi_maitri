 # Add these settings to your existing config.py

# Speech-to-Text Configuration
STT_SAMPLE_RATE = 16000
STT_CHUNK_SIZE = 1600  # 100ms chunks
STT_STREAMING_LIMIT = 240000  # 4 minutes in milliseconds
STT_DEFAULT_LANGUAGE = "en-US"
STT_MAX_ALTERNATIVES = 1

# WebSocket Configuration
WS_MAX_CONNECTIONS = 10
WS_HEARTBEAT_INTERVAL = 30  # seconds