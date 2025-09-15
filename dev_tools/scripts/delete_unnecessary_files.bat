@echo off
echo This script will delete the following files and directories:
echo - T:\Meu Drive\Caçula\Langchain\Agent_BI\__pycache__/
echo - T:\Meu Drive\Caçula\Langchain\Agent_BI\.mypy_cache/
echo - T:\Meu Drive\Caçula\Langchain\Agent_BI\.pytest_cache/
echo - T:\Meu Drive\Caçula\Langchain\Agent_BI\pytest-cache-files-l2wg2ocd/
echo - T:\Meu Drive\Caçula\Langchain\Agent_BI\venv/
echo - T:\Meu Drive\Caçula\Langchain\Agent_BI\desktop.ini
echo - T:\Meu Drive\Caçula\Langchain\Agent_BI\.github/desktop.ini
echo - T:\Meu Drive\Caçula\Langchain\Agent_BI\.github/workflows/desktop.ini
echo - T:\Meu Drive\Caçula\Langchain\Agent_BI\final_cleanup_temp.py
echo - T:\Meu Drive\Caçula\Langchain\Agent_BI\inspect_parquet.py
echo - T:\Meu Drive\Caçula\Langchain\Agent_BI\secao.txt

pause
echo Deleting directory: T:\Meu Drive\Caçula\Langchain\Agent_BI\__pycache__/
rmdir /s /q "T:\Meu Drive\Caçula\Langchain\Agent_BI\__pycache__/"
echo Deleting directory: T:\Meu Drive\Caçula\Langchain\Agent_BI\.mypy_cache/
rmdir /s /q "T:\Meu Drive\Caçula\Langchain\Agent_BI\.mypy_cache/"
echo Deleting directory: T:\Meu Drive\Caçula\Langchain\Agent_BI\.pytest_cache/
rmdir /s /q "T:\Meu Drive\Caçula\Langchain\Agent_BI\.pytest_cache/"
echo Deleting directory: T:\Meu Drive\Caçula\Langchain\Agent_BI\pytest-cache-files-l2wg2ocd/
rmdir /s /q "T:\Meu Drive\Caçula\Langchain\Agent_BI\pytest-cache-files-l2wg2ocd/"
echo Deleting directory: T:\Meu Drive\Caçula\Langchain\Agent_BI\venv/
rmdir /s /q "T:\Meu Drive\Caçula\Langchain\Agent_BI\venv/"
echo Deleting file: T:\Meu Drive\Caçula\Langchain\Agent_BI\desktop.ini
del /f /q "T:\Meu Drive\Caçula\Langchain\Agent_BI\desktop.ini"
echo Deleting file: T:\Meu Drive\Caçula\Langchain\Agent_BI\.github/desktop.ini
del /f /q "T:\Meu Drive\Caçula\Langchain\Agent_BI\.github/desktop.ini"
echo Deleting file: T:\Meu Drive\Caçula\Langchain\Agent_BI\.github/workflows/desktop.ini
del /f /q "T:\Meu Drive\Caçula\Langchain\Agent_BI\.github/workflows/desktop.ini"
echo Deleting file: T:\Meu Drive\Caçula\Langchain\Agent_BI\final_cleanup_temp.py
del /f /q "T:\Meu Drive\Caçula\Langchain\Agent_BI\final_cleanup_temp.py"
echo Deleting file: T:\Meu Drive\Caçula\Langchain\Agent_BI\inspect_parquet.py
del /f /q "T:\Meu Drive\Caçula\Langchain\Agent_BI\inspect_parquet.py"
echo Deleting file: T:\Meu Drive\Caçula\Langchain\Agent_BI\secao.txt
del /f /q "T:\Meu Drive\Caçula\Langchain\Agent_BI\secao.txt"

echo Cleanup complete.
pause
