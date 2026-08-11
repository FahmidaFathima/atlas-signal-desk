import os


def save_voice_file(audio_data: bytes, file_path: str) -> str:
    """Save Telegram voice audio to disk."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "wb") as file:
        file.write(audio_data)

    return file_path