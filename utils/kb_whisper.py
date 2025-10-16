"""
KB-Whisper integration för lokal svensk transkribering
Använder KBLab's Whisper-modeller som är tränade på 50,000 timmar svensk data
Ger 47% bättre resultat än OpenAI Whisper för svenska
"""

import os
import streamlit as st
import torch
from typing import Optional, Literal

# Global cache för modellen
_kb_whisper_model = None
_kb_whisper_processor = None
_kb_whisper_pipe = None

# Tillgängliga modeller från KBLab
KB_WHISPER_MODELS = {
    "large": "KBLab/kb-whisper-large",      # 2B parametrar - Bäst kvalitet
    "medium": "KBLab/kb-whisper-medium",    # 0.8B parametrar - Balans
    "small": "KBLab/kb-whisper-small",      # 0.3B parametrar - Snabbare
    "base": "KBLab/kb-whisper-base",        # 99M parametrar - Mycket snabb
    "tiny": "KBLab/kb-whisper-tiny"         # 57M parametrar - Snabbast
}

def get_kb_whisper_model_size():
    """Hämta vald modellstorlek från environment eller använd default"""
    return os.getenv('KB_WHISPER_MODEL', 'medium')

def get_kb_whisper_model_id():
    """Hämta model ID baserat på vald storlek"""
    size = get_kb_whisper_model_size()
    return KB_WHISPER_MODELS.get(size, KB_WHISPER_MODELS['medium'])

def get_transcription_style():
    """
    Hämta transkriberingsstil från environment
    - default: Standard transkribering
    - subtitle: Mer komprimerad stil
    - strict: Mer verbatim-lik
    """
    return os.getenv('KB_WHISPER_STYLE', 'default')

def load_kb_whisper_model():
    """
    Ladda KB-Whisper modellen i minnet (caching)
    Returnerar (model, processor, pipeline) eller None vid fel
    """
    global _kb_whisper_model, _kb_whisper_processor, _kb_whisper_pipe

    # Om modellen redan är laddad, returnera den
    if _kb_whisper_pipe is not None:
        return _kb_whisper_model, _kb_whisper_processor, _kb_whisper_pipe

    try:
        from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

        # Välj device (GPU om tillgängligt, annars CPU)
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        model_id = get_kb_whisper_model_id()
        style = get_transcription_style()

        st.info(f"🔄 Laddar KB-Whisper modell: {model_id} (stil: {style})")
        st.info(f"📊 Använder: {device.upper()}")

        # Ladda modellen med rätt revision om subtitle eller strict
        model_kwargs = {
            "torch_dtype": torch_dtype,
            "use_safetensors": True,
            "cache_dir": "cache"
        }

        if style in ["subtitle", "strict"]:
            model_kwargs["revision"] = style

        _kb_whisper_model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_id,
            **model_kwargs
        )
        _kb_whisper_model.to(device)

        # Ladda processor
        _kb_whisper_processor = AutoProcessor.from_pretrained(model_id)

        # Skapa pipeline
        _kb_whisper_pipe = pipeline(
            "automatic-speech-recognition",
            model=_kb_whisper_model,
            tokenizer=_kb_whisper_processor.tokenizer,
            feature_extractor=_kb_whisper_processor.feature_extractor,
            torch_dtype=torch_dtype,
            device=device,
        )

        st.success(f"✅ KB-Whisper modell laddad: {model_id}")

        return _kb_whisper_model, _kb_whisper_processor, _kb_whisper_pipe

    except Exception as e:
        st.error(f"❌ Kunde inte ladda KB-Whisper modell: {e}")
        st.warning("💡 Kontrollera att transformers och torch är installerade.")
        return None, None, None

def transcribe_with_kb_whisper(audio_file_path: str) -> Optional[str]:
    """
    Transkribera en ljudfil med KB-Whisper

    Args:
        audio_file_path: Sökväg till ljudfil

    Returns:
        Transkribering som sträng eller None vid fel
    """
    try:
        # Ladda modellen (cachas automatiskt)
        model, processor, pipe = load_kb_whisper_model()

        if pipe is None:
            return None

        # Transkribera med KB-Whisper
        # chunk_length_s=30 för att hantera långa filer effektivt
        generate_kwargs = {
            "task": "transcribe",
            "language": "sv"
        }

        with st.spinner(f"🎤 Transkriberar med KB-Whisper..."):
            result = pipe(
                audio_file_path,
                chunk_length_s=30,
                generate_kwargs=generate_kwargs
            )

        # Resultat är en dict med "text" key
        transcription = result.get("text", "")

        if transcription:
            st.success("✅ KB-Whisper transkribering klar!")
            return transcription
        else:
            st.error("❌ Ingen transkribering genererades")
            return None

    except Exception as e:
        st.error(f"❌ Fel vid KB-Whisper transkribering: {e}")
        return None

def unload_kb_whisper_model():
    """
    Frigör minne genom att ta bort modellen från RAM/VRAM
    Använd detta om du vill spara minne när modellen inte används
    """
    global _kb_whisper_model, _kb_whisper_processor, _kb_whisper_pipe

    if _kb_whisper_model is not None:
        del _kb_whisper_model
        del _kb_whisper_processor
        del _kb_whisper_pipe

        _kb_whisper_model = None
        _kb_whisper_processor = None
        _kb_whisper_pipe = None

        # Rensa CUDA cache om GPU används
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        st.info("🗑️ KB-Whisper modell borttagen från minnet")

def is_kb_whisper_available() -> bool:
    """
    Kontrollera om KB-Whisper dependencies är installerade
    """
    try:
        import transformers
        import torch
        import accelerate
        import librosa
        import soundfile
        return True
    except ImportError:
        return False

def get_kb_whisper_info() -> dict:
    """
    Hämta information om KB-Whisper konfigurationen
    """
    return {
        "available": is_kb_whisper_available(),
        "model_size": get_kb_whisper_model_size(),
        "model_id": get_kb_whisper_model_id(),
        "style": get_transcription_style(),
        "cuda_available": torch.cuda.is_available() if is_kb_whisper_available() else False,
        "loaded": _kb_whisper_pipe is not None
    }
