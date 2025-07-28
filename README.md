# PDF Outline Extractor

A Docker-based tool for extracting outlines/bookmarks from PDF files.

## Project Structure

```
challenge_1a/
├── src/
│   ├── pdf_extract.py          # Main extraction script
│   ├── tempCodeRunner.py       # Temporary runner
│   ├── extract_outline.py      # Outline extraction logic
│   └── requirements.txt        # Python dependencies
├── input/                      # Place your PDF files here
│   ├── .gitkeep               # Keeps directory in git
│   └── *.pdf                  # Your PDF files (not tracked)
├── output/                     # Extracted results appear here
│   └── .gitkeep               # Keeps directory in git
├── Dockerfile                 # Docker build configuration
├── README.md                  # This file
├── .gitignore                # Git ignore rules
└── .env.example              # Environment variables template
```

## Quick Start

### Prerequisites
- Docker installed on your system
- PDF files to process

### Usage

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd challenge_1a
   ```

2. **Place PDF files in the input directory:**
   ```bash
   cp your-files.pdf input/
   ```

3. **Build the Docker image:**
   ```bash
   docker build --platform linux/amd64 -t pdf-outline-extractor:latest .
   ```

4. **Run the extraction:**
   
   **For Git Bash (Windows):**
   ```bash
   export MSYS_NO_PATHCONV=1
   docker run --rm -v ${PWD}/input:/app/input -v ${PWD}/output:/app/output --network none pdf-outline-extractor:latest
   ```
   
   **For PowerShell (Windows):**
   ```powershell
   docker run --rm -v "${PWD}/input:/app/input" -v "${PWD}/output:/app/output" --network none pdf-outline-extractor:latest
   ```
   
   **For Linux/Mac:**
   ```bash
   docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none pdf-outline-extractor:latest
   ```

5. **Check results:**
   ```bash
   ls -la output/
   ```

## Development

### Local Development Setup

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r src/requirements.txt
   ```

3. **Run locally:**
   ```bash
   python src/pdf_extract.py
   ```

### Docker Development

**Build for development:**
```bash
docker build -t pdf-outline-extractor:dev .
```

**Run with interactive shell:**
```bash
docker run --rm -v ${PWD}/input:/app/input -v ${PWD}/output:/app/output -it pdf-outline-extractor:dev /bin/bash
```

## Troubleshooting

### Common Issues

1. **"No PDF files found" error:**
   - Ensure PDF files are in the `input/` directory
   - Check that you're running Docker from the project root
   - Verify volume mounts with: `docker run --rm -v ${PWD}/input:/app/input -it pdf-outline-extractor:latest ls -la /app/input`

2. **Path conversion issues (Windows Git Bash):**
   ```bash
   export MSYS_NO_PATHCONV=1
   ```

3. **Permission issues:**
   ```bash
   chmod -R 755 input/ output/
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with Docker
5. Submit a pull request

---