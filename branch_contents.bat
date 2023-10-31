@echo off
SETLOCAL EnableDelayedExpansion

REM Fetch all remote branches (optional)
git fetch

REM Loop through all branches
FOR /F "tokens=*" %%b IN ('git branch -a ^| findstr /V HEAD') DO (
    echo ===== Branch: %%b =====
    
    REM Get the list of all files and directories in the branch
    FOR /F "tokens=*" %%f IN ('git ls-tree -r --name-only "%%b"') DO (
        echo %%f
    )

    echo.
)

ENDLOCAL
