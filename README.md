# ✨ AI Media & Speech Studio

A comprehensive, all-in-one Python and Streamlit studio that unifies **3 multimedia generation tools** in a single application:

1. 🗣️ **Text to Speech (TTS)**: Convert any text to natural spoken voice with voice selection, rate and volume controls, instant browser playback, and WAV audio download (powered locally by `pyttsx3` / SAPI5).
2. 🖼️ **Text to Image**: Generate photorealistic and artistic images from text prompts using **FLUX.1 Schnell** via fal.ai.
3. 🎬 **Text to Video**: Generate high-definition AI videos from text prompts and camera motion descriptions using **Wan 2.7** via fal.ai.

---

## 📁 Project Structure

```text
Speech/
├── app.py                # Main Streamlit unified application (3 tabs: TTS, Image, Video)
├── Speech.py             # Standalone Python CLI script for Text-to-Speech
├── tts_engine.py         # Modular TTS helper handling voice listing & WAV audio synthesis
├── requirements.txt      # Python dependencies
├── .env.example          # Sample environment variables file
├── .env                  # Your private API keys (never commit)
├── .gitignore            # Git ignore rules
└── outputs/              # Automatically created folder saving generated audio, images & videos
```

---

## 🚀 Getting Started

### 1. Requirements
- Python 3.10 or newer
- Windows, macOS, or Linux
- A [fal.ai](https://fal.ai) API key for Image & Video generation (Text-to-Speech runs 100% locally with no API key needed!)

### 2. Setup & Installation (Windows PowerShell)

```powershell
# Navigate to the project directory
cd c:\Coding\Speech

# (Optional but recommended) Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure API Key (for Image & Video)
Copy `.env.example` to `.env` (or edit the existing `.env`):
```powershell
Copy-Item .env.example .env
```
Open `.env` and set your key:
```env
FAL_KEY=your_actual_fal_key_here
```
*(You can also paste the key directly into the app sidebar while running!)*

---

## 💻 How to Run

### Option A: Launch the Unified Web Application (Recommended)

Run:
```powershell
streamlit run app.py
```
Open your browser to the local URL (usually `http://localhost:8501`).

You will have access to all 3 tools in one place:
- **🗣️ Tab 1 (Text to Speech)**: Select voice, speed, volume -> Generate speech, listen directly in the web browser, and download the `.wav` file.
- **🖼️ Tab 2 (Text to Image)**: Choose aspect ratio & count -> Generate images using FLUX.1 -> Preview and download `.png`.
- **🎬 Tab 3 (Text to Video)**: Set aspect ratio, duration & resolution -> Generate video with Wan 2.7 -> Watch preview and download `.mp4`.

All generated files are automatically backed up in the `outputs/` folder!

---

### Option B: Run Standalone Text-to-Speech CLI (`Speech.py`)

You can also run the command-line script directly:
```powershell
python Speech.py
```
1. It lists available voices installed on your system.
2. Select your preferred voice index (or hit Enter for default).
3. Type the text you want spoken.
4. It speaks through your computer's speakers and saves `output.wav`.

---

## 🛠️ Models & Endpoints

| Capability | Model / Engine | Provider / Library | Notes |
| :--- | :--- | :--- | :--- |
| **Text to Speech** | SAPI5 / Windows Speech | `pyttsx3` / local | Zero API cost, runs offline, exports WAV |
| **Text to Image** | FLUX.1 Schnell | `fal-ai/flux/schnell` | Fast 4-step diffusion, customizable aspect ratios |
| **Text to Video** | Wan 2.7 Text-to-Video | `fal-ai/wan/v2.7/text-to-video` | 720p/1080p cinematic video clips |
