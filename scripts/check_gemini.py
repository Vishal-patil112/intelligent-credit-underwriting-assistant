from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.llm import GeminiClient

client = GeminiClient()
if not client.enabled:
    raise SystemExit('GEMINI_API_KEY is not configured. Add it to .env first.')
print(client.generate_text('Reply exactly with GEMINI_CONNECTION_OK'))
