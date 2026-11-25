import os
import torch
import soundfile as sf

def test_kokoro():
    print("Testing Kokoro TTS...")
    print("PyTorch version:", torch.__version__)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("Device:", device)
    
    try:
        from kokoro import KPipeline
        print("Initializing KPipeline for lang_code='a'...")
        pipeline = KPipeline(lang_code='a', device=device)
        print("Pipeline initialized successfully!")
        
        text = "Hello! This is Kokoro, an open source AI text to speech model running locally."
        print(f"Synthesizing text: '{text}' with voice='af_heart'...")
        
        generator = pipeline(text, voice='af_heart', speed=1.0)
        
        all_audio = []
        for i, (gs, ps, audio) in enumerate(generator):
            print(f"Chunk {i}: graphemes={gs}, audio shape={audio.shape}")
            all_audio.append(audio)
            
        if all_audio:
            import numpy as np
            combined = np.concatenate(all_audio) if isinstance(all_audio[0], np.ndarray) else torch.cat(all_audio).numpy()
            os.makedirs("outputs", exist_ok=True)
            out_file = "outputs/test_kokoro.wav"
            sf.write(out_file, combined, 24000)
            print(f"Success! Kokoro generated audio saved to: {out_file} (size: {os.path.getsize(out_file)} bytes)")
        else:
            print("No audio chunks generated.")
    except Exception as e:
        print("Kokoro error:", type(e), e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_kokoro()
