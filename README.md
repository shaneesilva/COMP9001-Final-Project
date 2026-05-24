<img width="1080" height="1350" alt="PIXEL PET PLANNER" src="https://github.com/user-attachments/assets/f566bb37-f144-4bf9-86c8-5da2b7cbcb37" />


# Pixel Pet Planner

Pixel Pet Planner is a colorful to-do list web app written with a Python standard-library backend and a pixel-art HTML/CSS/JavaScript frontend. The user logs into a 2D flip phone, opens today's to-do list, and keeps a pixel cat happy by completing tasks.

Five completed tasks in one day fills the cat's bowl. If the user has unfinished tasks and does not complete anything, the cat becomes hungry or sleepy.

## AI usage disclosure
Majority of the python file `main.py` was written by myself. However, AI tools were used in the ideation and planning phase of this project, such as identifying all the files, libraries and tools needed to create this project. For `main.py` the parts/concepts that required AI assistance has been noted and explained.

Furthermore, since i have expanded the scope of the project a bit wider than recommended, i would also like to disclose that the .json, .html, .css files were created with the assistance of AI since my knowledge in these languages are low, and are needed to wrap the project up and achieve my vision. 

The 2D Pixel assets were found by me online, and has been credited at the end of this file.

## How to Run

Unzip folder and navigate to directory, either set up virtual env or run locally:

```bash
python3 main.py
```

Open this URL in a browser:

```text
http://127.0.0.1:8000
```

If port 8000 is busy, run a different port:

```bash
python3 main.py --port 8001
```

No third-party Python packages are required.

## Optional Test Check

```bash
python3 -m unittest tests/test_app_logic.py
```


## Project Features

- Flip-phone login screen before the main app opens.
- Add, complete, delete, refresh, and clear completed daily tasks.
- Saved task data using JSON file I/O in `data/pixel_pet_tasks.json`.
- Pixel-art cat changes mood based on task progress.
- Five daily tasks are enough to feed the cat fully.
- Responsive colorful interface for desktop and mobile.

## Advanced Concepts Used

- **I/O system:** `main.py` reads and writes task data through `read_data()` and `write_data()`.
- **Recursion:** `recursive_tasks_for_day()` filters today's tasks, and `recursive_count_completed()` counts completed tasks.
- **Multi-dimensional lists:** `CAT_MOOD_GRID` is a nested list where rows represent urgency and columns represent completed task count.
- **Flow control:** `cat_urgency_row()` uses `if`, `elif`-style branching logic to decide the cat's mood.


## File Guide

- `main.py` - Python web server, API routes, persistence, recursion, and cat mood logic.
- `static/index.html` - Flip-phone login and app structure.
- `static/styles.css` - Pixel-art visual design and responsive layout.
- `static/app.js` - Browser interactivity and pixel cat rendering.
- `static/assets/cat-orange-spritesheet.png` - User-provided animated cat sprite sheet.
- `data/` - Saved JSON data appears here after the app runs.

## Asset Credits

The animated cat sprite sheet was added from the user-provided `Free pack.zip`.
This is the reference for te free resource: https://last-tick.itch.io/animated-pixel-cats-64x64
