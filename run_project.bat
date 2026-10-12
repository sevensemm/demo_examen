@echo off
chcp 65001 > nul

echo [1/3] Активация виртуального окружения...
call .demo_ex_venv\Scripts\activate.bat

echo [2/3] Переход в рабочую папку со скриптами...
cd /d "%~dp0scr"

echo [3/4] Инициализация базы данных и импорт данных...
python init_db.py
if %errorlevel% neq 0 (echo Ошибка при инициализации БД! & pause & exit /b)

python import_data.py
if %errorlevel% neq 0 (echo Ошибка при импорте данных из Excel! & pause & exit /b)

echo [4/4] Запуск веб-приложения Streamlit...
streamlit run app.py

pause
