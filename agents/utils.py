from typing import Dict, Any
from datetime import datetime

def format_agent_response(response: Dict[str, Any]) -> str:
    """
    Standardizes agent/tool responses with a timestamp. 
    Handles errors and skips metadata fields.

    Args:
        response (dict): Raw response from an agent/tool.

    Returns:
        str: Formatted string (timestamped), suitable for displaying in logs or UI.
    """
    try:
        timestamp = datetime.now().isoformat()

        # Error display if present
        if response is None:
            return f"[ERROR {timestamp}] Empty response."
        if "error" in response:
            return f"[ERROR {timestamp}] {response['error']}"

        formatted = []
        for key in sorted(response.keys()):
            if key.lower() in {"timestamp", "internal", "context", "meta"}:
                continue  # Hide technical/meta

            value = response[key]
            if isinstance(value, list):
                formatted.append(f"{key}: {', '.join(map(str, value))}")
            elif isinstance(value, dict):
                inner = ', '.join(f"{k}={v}" for k, v in value.items())
                formatted.append(f"{key}: {{{inner}}}")
            else:
                formatted.append(f"{key}: {value}")

        return f"[{timestamp}] " + " | ".join(formatted)
    except Exception as e:
        return f"[{datetime.now().isoformat()}] Formatting error: {str(e)}"

def validate_time_slot(slot: str) -> bool:
    """
    Validates a time slot string in the format "HH:MM-HH:MM".

    Args:
        slot (str): Time range string.

    Returns:
        bool: True if valid and start < end, else False.
    """
    try:
        if not isinstance(slot, str):
            return False

        slot = slot.strip()
        start_end = slot.split('-')
        if len(start_end) != 2:
            return False

        start_time_str, end_time_str = [t.strip() for t in start_end]

        def is_valid_time(t: str) -> bool:
            parts = t.split(':')
            if len(parts) != 2:
                return False
            hour, minute = int(parts[0]), int(parts[1])
            return 0 <= hour <= 23 and 0 <= minute <= 59

        if not is_valid_time(start_time_str) or not is_valid_time(end_time_str):
            return False

        # Optionally: Ensure start < end
        start_dt = datetime.strptime(start_time_str, "%H:%M")
        end_dt = datetime.strptime(end_time_str, "%H:%M")
        if start_dt >= end_dt:
            return False

        return True
    except Exception:
        return False
