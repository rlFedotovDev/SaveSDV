# SaveSDV

SaveSDV is a simple save editor for Stardew Valley made with Python and Lua.
It currently can edit the player name, the farm name and the money count.


# Building SaveSDV with PyInstaller

SaveSDV can be packaged into a standalone Windows executable using [PyInstaller](https://pyinstaller.org/).

The resulting `.exe` includes Python and the required Python dependencies, so **Python does not need to be installed on the target computer**.

## Requirements

* Windows 10 or later
* Python 3.10 or newer
* pip
* Git (optional)
* SaveSDV source code

It is recommended to build the Windows version on Windows. PyInstaller is not a cross-compiler.

## 1. Clone the repository

```bash
git clone https://github.com/rlFedotovDev/SaveSDV.git
cd SaveSDV
```

Or download the source code from GitHub and open a terminal in the project directory.

## 2. Create a virtual environment

Creating a virtual environment is recommended so that the SaveSDV dependencies do not interfere with other Python projects.

```bash
python -m venv .venv
```

Activate it:

### Command Prompt

```cmd
.venv\Scripts\activate
```

### PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

## 3. Install dependencies

Install the required packages:

```bash
pip install -r requirements.txt
```

Then install PyInstaller:

```bash
pip install pyinstaller
```

You can verify the installation with:

```bash
pyinstaller --version
```

## 4. Build SaveSDV

For the PyQt6 version:

```bash
pyinstaller --onefile --windowed --name SaveSDV savesdv_pyqt6.py
```

The executable will be created in:

```text
dist/SaveSDV.exe
```

You can run it with:

```cmd
dist\SaveSDV.exe
```

## 5. Including the GitHub icon

SaveSDV uses the GitHub SVG icon from:

```text
assets/github.svg
```

If the application needs this file at runtime, include it in the PyInstaller build:

```bash
pyinstaller --onefile --windowed --name SaveSDV --add-data "assets/github.svg;assets" savesdv_pyqt6.py
```

On Windows, PyInstaller uses `;` to separate the source and destination paths in `--add-data`.

The resulting executable will still be located at:

```text
dist/SaveSDV.exe
```

## 6. Building with a `.spec` file

For more control over the build, a PyInstaller `.spec` file can be used.

Example:

```python
a = Analysis(
    ["savesdv_pyqt6.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("assets/github.svg", "assets"),
    ],
    hiddenimports=[],
    ...
)
```

Then build using:

```bash
pyinstaller SaveSDV.spec
```

This is recommended for release builds because additional assets and configuration can be kept in one place.

## 7. PyQt5 version

SaveSDV also includes a PyQt5 version.

Build it with:

```bash
pyinstaller --onefile --windowed --name SaveSDV-PyQt5 savesdv_pyqt5.py
```

The executable will be:

```text
dist/SaveSDV-PyQt5.exe
```

## 8. Tkinter version

The Tkinter version can be built with:

```bash
pyinstaller --onefile --windowed --name SaveSDV-Tk savesdv_tk.py
```

The executable will be:

```text
dist/SaveSDV-Tk.exe
```

Tkinter is normally included with the standard Windows Python installation.

## 9. Clean build

If you encounter problems during a rebuild, remove the previous build files:

```cmd
rmdir /s /q build
rmdir /s /q dist
del /q SaveSDV.spec
```

Then run the PyInstaller command again.

Alternatively, use:

```bash
pyinstaller --clean --onefile --windowed --name SaveSDV --add-data "assets/github.svg;assets" savesdv_pyqt6.py
```

## 10. Testing the executable

Before releasing SaveSDV, test the generated `.exe` on a Windows computer where Python is **not installed**.

This helps verify that:

* Python is correctly bundled.
* PyQt6 works correctly.
* The GitHub icon is included.
* Save files can be opened.
* Backups are created before editing.
* The application can detect modded saves.
* Saving changes works correctly.

## Release build

A typical release build command is:

```bash
pyinstaller --clean --onefile --windowed --name SaveSDV --add-data "assets/github.svg;assets" savesdv_pyqt6.py
```

The final executable will be:

```text
dist/
└── SaveSDV.exe
```

You can then distribute `SaveSDV.exe` without requiring users to install Python.

> **Note:** PyInstaller bundles the Python interpreter and dependencies into the application. The source code is not required to run the compiled executable.

### Recommended target

The official Windows build targets:

**Windows 10 or later (64-bit)**
