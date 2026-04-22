import os
import subprocess
import torch
import torchaudio
from django.conf import settings
from .ml_models.models_ml import TranscribeModel, Tokenizer

# Load model and tokenizer
MODEL_PATH = os.path.join(settings.BASE_DIR, 'journals', 'ml_models', 'epoch_0.pt')
TOKENIZER_PATH = os.path.join(settings.BASE_DIR, 'journals', 'ml_models', 'tokenizer.json')

_tokenizer = Tokenizer(TOKENIZER_PATH)
_asr_model = TranscribeModel.load(MODEL_PATH, device='cpu')
_asr_model.eval()

def get_transcription(file_path):
    ffmpeg_exe = r"C:\ffmpeg-8.1-full_build-shared\bin\ffmpeg.exe"
    
    # Explicitly stream raw 16-bit PCM bytes directly from FFmpeg to bypass ALL torchaudio dependencies natively!
    process = subprocess.Popen(
        [ffmpeg_exe, '-y', '-i', file_path, '-f', 's16le', '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', '-'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    raw_audio, err_bytes = process.communicate()
    
    if process.returncode != 0:
        raise RuntimeError(f"FFmpeg crash internal error: {err_bytes.decode('utf-8', errors='ignore')}")
        
    if len(raw_audio) == 0:
        raise RuntimeError("FFmpeg returned an empty audio stream. The recording might have been 0 seconds long or corrupted.")
    
    # Convert raw memory bytes straight into a PyTorch tensor
    import array
    audio_array = array.array('h', raw_audio)  # 'h' is signed 16-bit integer
    waveform = torch.tensor(audio_array, dtype=torch.float32) / 32768.0
    waveform = waveform.unsqueeze(0) # [1, Time]
    sr = 16000
        
    # Run Model
    with torch.no_grad():
        # model expects [Batch, Time]
        log_probs, _ = _asr_model(waveform)
        arg_maxes = torch.argmax(log_probs, dim=-1)
        text = _tokenizer.decode(arg_maxes[0].tolist())
        
    if not text or len(text.strip()) == 0:
        text = "[Model heard silence or couldn't understand]"
        
    return text