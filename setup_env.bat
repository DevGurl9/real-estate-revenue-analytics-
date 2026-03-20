@echo off

echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Checking installed packages...
pip list

echo.
echo Checking outdated packages...
pip list --outdated

echo.
echo Upgrading packages...
pip install --upgrade pandas numpy matplotlib seaborn jupyter sqlalchemy

echo.
echo Saving requirements.txt...
pip freeze > requirements.txt

echo.
echo Done!
pause
