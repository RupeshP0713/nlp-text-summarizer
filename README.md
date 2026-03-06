# NLP Text Summarizer (Tkinter)

## Project Description
This project is a desktop NLP text summarizer built with Python and Tkinter.  
It summarizes free-form text using sentence ranking (PageRank over a similarity graph), supports keyword boosting, bullet/paragraph output modes, and light/dark themes.

## Features
- Text summarization using `nltk + numpy + networkx`
- Paragraph mode and bullet-point mode
- Keyword chips to prioritize important terms
- Summary length slider
- Paraphrase summary output
- Copy and download summary
- Light/Dark theme toggle

## Project Structure
```text
NLP/
|-- app/
|   |-- __init__.py
|   |-- core/
|   |   |-- __init__.py
|   |   `-- nlp_engine.py
|   `-- ui/
|       |-- __init__.py
|       |-- theme.py
|       `-- main_window.py
|-- main.py
|-- req.txt
`-- venv/
```

## Requirements
- Python 3.10+ (3.12 works)
- `pip`

Dependencies are listed in `req.txt`:
- `nltk>=3.8`
- `numpy>=1.24`
- `networkx>=3.0`

## Installation
1. Open terminal in project folder:
   ```powershell
   cd "d:\All Files\Project\NLP"
   ```
2. Create virtual environment:
   ```powershell
   python -m venv venv
   ```
3. Activate virtual environment (Windows):
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
4. Install dependencies:
   ```powershell
   pip install -r req.txt
   ```

## Run the App
```powershell
python main.py
```

## Notes
- On first run, the app tries to download required NLTK resources (`punkt`, `punkt_tab`, `stopwords`, `wordnet`).
- Make sure you have internet access on first launch for NLTK data download.

## Troubleshooting
- If NLTK tokenizer/corpus errors appear, run:
  ```powershell
  python -c "import nltk; [nltk.download(x) for x in ['punkt','punkt_tab','stopwords','wordnet']]"
  ```
- If PowerShell blocks venv activation, run:
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  ```
