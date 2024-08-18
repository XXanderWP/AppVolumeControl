@echo off
setlocal

:: Отобразить последнюю версию (последний тег)
echo Latest version:
git describe --tags --abbrev=0

:: Запросить версию у пользователя
set /p version="Enter new version (e.g., v1.0.1): "

:: Проверка на пустое значение
if "%version%"=="" (
    echo Version cannot be empty.
    exit /b 1
)

:: Создать новый тег
git tag %version%

:: Отправить новый тег в удаленный репозиторий
git push origin %version%

echo Tag %version% created and pushed successfully.

endlocal
pause
