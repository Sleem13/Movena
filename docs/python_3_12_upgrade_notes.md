# Python 3.12 Upgrade Notes

## Upgrade Rationale

PhysioVision AI moved to Python 3.12 to use a current, supported Python runtime with newer language/runtime improvements and current binary wheels across the project’s FastAPI, MediaPipe, OpenCV, pandas, scikit-learn, ReportLab, and testing stack. The upgrade also removes dependence on older external virtual environments whose launchers and installed packages had become inconsistent.

This was an environment validation change only. Application logic, model training behavior, thresholds, APIs, and architecture were not changed as part of the upgrade review.

## Validated Runtime

The project-local interpreter reports:

```text
Python 3.12.10
C:\Users\Admin\Documents\GitHub\PhysioVision-AI\.venv\Scripts\python.exe
```

Always confirm both version and executable path:

```powershell
python -c "import sys; print(sys.version); print(sys.executable)"
```

The executable should be inside this repository’s `.venv`. During validation, an unqualified `python` in one shell resolved incorrectly to `D:\AI tools\venv\Scripts\python.exe` on Python 3.11.0. That external environment had missing and incompatible dependencies and must not be used for this project.

## Installation Notes

Install a 64-bit Python 3.12 release and confirm its launcher registration:

```powershell
py -0p
py -3.12 -c "import sys; print(sys.version); print(sys.executable)"
```

If `py -3.12` is unavailable, install Python 3.12 first or invoke the installed Python 3.12 executable by its full path when creating the environment.

## Clean Virtual Environment Reset

Close processes using the old environment. From the repository root, remove only the project-local `.venv`, then recreate it:

```powershell
deactivate  # if an environment is active; ignore if unavailable
Remove-Item -LiteralPath .venv -Recurse -Force
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Before removing `.venv`, verify the current directory is the PhysioVision AI repository. Do not remove or reuse virtual environments belonging to other projects.

If local policy blocks PowerShell scripts, do not rely on activation. Run the project interpreter explicitly:

```powershell
.\.venv\Scripts\python.exe -c "import sys; print(sys.version); print(sys.executable)"
```

## Dependency Installation

With the project interpreter selected:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m pip check
```

Direct-interpreter fallback:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pip check
```

Do not copy `site-packages` from a Python 3.11 environment. Native wheels and environment launchers must be installed fresh for Python 3.12.

## Validation Commands

After selecting the project-local interpreter:

```powershell
python -c "import sys; print(sys.version); print(sys.executable)"
python -m pip check
python -m pytest
```

When activation is unavailable:

```powershell
.\.venv\Scripts\python.exe -c "import sys; print(sys.version); print(sys.executable)"
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pytest
```

Validation result on Python 3.12.10: **50 tests passed**.

## Compatibility Notes

- FastAPI, Pydantic, OpenCV, MediaPipe, pandas, NumPy, scikit-learn, ReportLab, joblib, and the project test client loaded successfully under Python 3.12.10.
- The complete backend, dataset, ML baseline, artifact, and augmentation test suite passed.
- Two scikit-learn test paths emit an upstream SciPy deprecation warning about L-BFGS-B `disp`/`iprint` options. This is non-blocking and is expected to be resolved by future dependency releases before SciPy 1.18 removes those options.
- Saved joblib/scikit-learn artifacts should be regenerated or revalidated whenever Python or scikit-learn versions change, and they must only be loaded from trusted project files.
- PowerShell may block `.venv\Scripts\Activate.ps1` under restrictive execution policy. Directly invoking `.venv\Scripts\python.exe` is a safe alternative and does not require changing system policy.
- A successful `pytest` command from the wrong interpreter is not meaningful. Always inspect `sys.executable` first.
