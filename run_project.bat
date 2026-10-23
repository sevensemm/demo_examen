@echo off
cd /d "%~dp0"

IF NOT EXIST ".demo_ex_venv\Scripts\activate.bat" (
    echo [1/4] Создание виртуального окружения...
    python -m venv .demo_ex_venv
)

echo [2/4] Активация и установка зависимостей...
call .demo_ex_venv\Scripts\activate.bat
pip install -r requirements.txt

echo [3/4] Инициализация БД и импорт данных...
cd scr
python init_db.py
if %errorlevel% neq 0 (echo Ошибка init_db & pause & exit /b)
python import_data.py
if %errorlevel% neq 0 (echo Ошибка import_data & pause & exit /b)

echo [4/4] Запуск Streamlit...
streamlit run app.py
pause