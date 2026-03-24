@echo off

echo ===============================
echo Launching Jupyter Notebook
echo ===============================

REM Go to your project folder (important for OneDrive paths)
cd /d "C:\Users\kim_k\OneDrive\Documents\edu2019\python\Projects\real-estate-revenue-analytics"

echo.
echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Starting Jupyter Notebook...
REM jupyter notebook
jupyter notebook --notebook-dir="C:\Users\kim_k\OneDrive\Documents\edu2019\python\Projects\real-estate-revenue-analytics"

echo.
echo Jupyter closed.
pause
