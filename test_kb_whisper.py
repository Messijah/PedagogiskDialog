"""
Test script för KB-Whisper integration
Kör detta script för att verifiera att KB-Whisper är korrekt installerat
"""

import sys
import os

def test_imports():
    """Testa att alla dependencies är installerade"""
    print("🔍 Testar dependencies...")

    required_packages = {
        'transformers': 'Hugging Face Transformers',
        'torch': 'PyTorch',
        'accelerate': 'Accelerate',
        'librosa': 'Librosa',
        'soundfile': 'SoundFile'
    }

    missing = []
    for package, name in required_packages.items():
        try:
            __import__(package)
            print(f"  ✅ {name} ({package}) - OK")
        except ImportError:
            print(f"  ❌ {name} ({package}) - SAKNAS")
            missing.append(package)

    if missing:
        print(f"\n⚠️  Saknade paket: {', '.join(missing)}")
        print(f"💡 Installera med: pip install {' '.join(missing)}")
        return False

    print("\n✅ Alla dependencies installerade!\n")
    return True

def test_gpu():
    """Testa om GPU är tillgänglig"""
    print("🖥️  Testar GPU-tillgänglighet...")

    try:
        import torch

        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            print(f"  ✅ GPU tillgänglig: {gpu_name}")
            print(f"  📊 CUDA Version: {torch.version.cuda}")
            print(f"  💾 VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
            return True
        else:
            print("  ⚠️  Ingen GPU hittades - kommer använda CPU")
            print("  💡 CPU-körning är långsammare men fungerar för alla modellstorlekar utom 'large'")
            return False
    except Exception as e:
        print(f"  ❌ Fel vid GPU-test: {e}")
        return False

def test_kb_whisper_module():
    """Testa KB-Whisper modulen"""
    print("\n🎤 Testar KB-Whisper modul...")

    try:
        from utils.kb_whisper import (
            is_kb_whisper_available,
            get_kb_whisper_info,
            get_kb_whisper_model_size,
            get_kb_whisper_model_id,
            get_transcription_style
        )

        print("  ✅ KB-Whisper modul importerad OK")

        # Testa funktioner
        available = is_kb_whisper_available()
        print(f"  ✅ is_kb_whisper_available(): {available}")

        if available:
            info = get_kb_whisper_info()
            print(f"  ✅ KB-Whisper info:")
            print(f"     - Model size: {info['model_size']}")
            print(f"     - Model ID: {info['model_id']}")
            print(f"     - Style: {info['style']}")
            print(f"     - CUDA: {info['cuda_available']}")
            print(f"     - Loaded: {info['loaded']}")

        return True
    except Exception as e:
        print(f"  ❌ Fel vid KB-Whisper modultest: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_audio_handler():
    """Testa audio_handler integration"""
    print("\n🔊 Testar audio_handler integration...")

    try:
        from utils.audio_handler import (
            get_transcription_backend,
            transcribe_audio_file
        )

        print("  ✅ audio_handler importerad OK")

        backend = get_transcription_backend()
        print(f"  ✅ Vald backend: {backend}")

        if backend == 'kb-whisper':
            print("  ℹ️  KB-Whisper är aktiverat i .env")
        else:
            print("  ℹ️  OpenAI Whisper är aktiverat i .env")
            print("  💡 För att testa KB-Whisper, sätt TRANSCRIPTION_BACKEND=kb-whisper i .env")

        return True
    except Exception as e:
        print(f"  ❌ Fel vid audio_handler test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_env_configuration():
    """Testa environment configuration"""
    print("\n⚙️  Testar .env konfiguration...")

    from dotenv import load_dotenv
    load_dotenv()

    backend = os.getenv('TRANSCRIPTION_BACKEND', 'openai')
    print(f"  ✅ TRANSCRIPTION_BACKEND: {backend}")

    if backend == 'kb-whisper':
        model = os.getenv('KB_WHISPER_MODEL', 'medium')
        style = os.getenv('KB_WHISPER_STYLE', 'default')

        print(f"  ✅ KB_WHISPER_MODEL: {model}")
        print(f"  ✅ KB_WHISPER_STYLE: {style}")

        valid_models = ['tiny', 'base', 'small', 'medium', 'large']
        valid_styles = ['default', 'subtitle', 'strict']

        if model not in valid_models:
            print(f"  ⚠️  Ogiltig modell '{model}'. Giltiga: {', '.join(valid_models)}")

        if style not in valid_styles:
            print(f"  ⚠️  Ogiltig stil '{style}'. Giltiga: {', '.join(valid_styles)}")

    return True

def run_all_tests():
    """Kör alla tester"""
    print("=" * 60)
    print("🧪 KB-Whisper Integration Test")
    print("=" * 60)
    print()

    results = []

    # Test 1: Dependencies
    results.append(("Dependencies", test_imports()))

    # Test 2: GPU
    results.append(("GPU", test_gpu()))

    # Test 3: KB-Whisper modul
    results.append(("KB-Whisper modul", test_kb_whisper_module()))

    # Test 4: Audio handler
    results.append(("Audio handler", test_audio_handler()))

    # Test 5: Environment
    results.append(("Environment config", test_env_configuration()))

    # Sammanfattning
    print("\n" + "=" * 60)
    print("📊 TESTRESULTAT")
    print("=" * 60)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    all_passed = all(result for _, result in results)

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALLA TESTER SLUTFÖRDA MED FRAMGÅNG!")
        print("\n💡 Nästa steg:")
        print("   1. Sätt TRANSCRIPTION_BACKEND=kb-whisper i .env")
        print("   2. Starta applikationen: streamlit run main.py")
        print("   3. Testa transkribering med en ljudfil")
        print("\n📖 Läs KB_WHISPER_GUIDE.md för mer information")
    else:
        print("⚠️  NÅGRA TESTER MISSLYCKADES")
        print("\n💡 Åtgärder:")
        print("   1. Installera saknade dependencies: pip install -r requirements.txt")
        print("   2. Kontrollera .env konfiguration")
        print("   3. Läs KB_WHISPER_GUIDE.md för felsökning")
    print("=" * 60)

    return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
