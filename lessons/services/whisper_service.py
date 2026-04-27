from faster_whisper import WhisperModel

_model = None


def get_whisper_model():
    global _model
    if _model is None:
        _model = WhisperModel("base", device="cpu", compute_type="int8")
    return _model


def transcribe_audio(audio_path: str) -> str:
    model = get_whisper_model()

    segments, info = model.transcribe(
        audio_path,
        beam_size=5,
    )

    text = "".join(segment.text for segment in segments).strip()
    return text
