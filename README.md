# Kakurasu Game With AI Solver

Kakurasu is a grid-based puzzle game implemented with Pygame. The project includes both manual gameplay and AI-assisted solving logic.

## Preview

![Kakurasu UI](UI/image%201.png)

## Features

- Randomized puzzle generation
- Interactive click-based gameplay
- AI solving support
- Solution validation and reveal behavior
- Visual interface with labeled grid and clue sums

## Tech Stack

- Python
- Pygame

## Requirements

- Python 3.10+
- Pygame
- GNU Make

## Quick Start (with Makefile)

From the repository root:

```bash
make install
```

Activate the virtual environment:

```bash
make activate
```

Then run the printed command in your shell:

- PowerShell: `.\\.venv\\Scripts\\Activate.ps1`
- Bash: `source .venv/bin/activate`

To deactivate later:

```bash
make deactivate
```

Run the game:

```bash
make run
```

## Manual dependency install (without Makefile)

If you prefer not to use Make, install dependencies from the project folder:

```bash
cd kakurasu/Kakurasu-Game-With-AI-Solver-Using-Search-Algorithm
pip install -r requirements.txt
```

## Run

From the project folder:

```bash
cd kakurasu/Kakurasu-Game-With-AI-Solver-Using-Search-Algorithm
python main.py
```

## Project Files

- `main.py`: Main game loop, rendering, and AI logic
- `images/`: Sprite and UI assets used by the game
- `UI/`: Additional interface resources

## Notes

- Run commands from this directory so image paths resolve correctly.
- If the game window does not appear, verify Pygame installation and local graphics support.

## Acknowledgments

Special thanks to this repository for helpful ideas and references during development:

- https://github.com/ERJ00/Kakurasu-Game-With-AI-Solver-Using-Propositional-Logic/
