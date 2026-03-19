# BTL1 NMAI - AI Puzzle Solvers

This repository contains two Python projects built for AI coursework:

- `kakurasu/Kakurasu-Game-With-AI-Solver-Using-Searchings-Algorithm`: Kakurasu puzzle game with an AI solver
- `pipes/`: Pipes puzzle visualizer and AI solver (DFS and A*) with level conversion tools

## Repository Structure

```text
kakurasu/
  Kakurasu-Game-With-AI-Solver-Using-Searchings-Algorithm/
```

## Requirements

- Python 3.10+
- `pip`
- `pygame`
- Optional for web scraping in Pipes: `requests`

## Quick Start

### 1) Clone

```bash
git clone <your-repository-url>
cd BTL1_NMAI_Nhom8
```

### 2) Run Kakurasu

```bash
cd kakurasu/Kakurasu-Game-With-AI-Solver-Using-Searchings-Algorithm
pip install -r requirements.txt
python main.py
```

## Project Guides

- Kakurasu guide: `kakurasu/Kakurasu-Game-With-AI-Solver-Using-Searchings-Algorithm/README.md`
- Pipes converter details: `pipes/AUTO_SCRAPER_README.md`

## Common Issues

- If `pygame` fails to install, update pip first:

```bash
python -m pip install --upgrade pip
```

- If the game window opens but assets are missing, run the command from the project folder (not from repository root).

## For GitHub Visitors

To make this repository easier for others to evaluate:

- Include screenshots or short demo GIFs in each project README.
- Keep sample inputs in `pipes/inputs` for reproducible results.
- Add problem statements, expected output, and algorithm notes in pull requests.
