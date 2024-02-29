@echo off
setlocal

rem Initialize the current directory variable
set "currentDir=%~dp0"

rem Navigate up the directory tree until we find the Bench_Repo directory
:findRepo
if exist "%currentDir%\Bench_Repo" (
    set "baseDir=%currentDir%"
) else (
    cd /d "%currentDir%\.."
    set "currentDir=%cd%"
    goto :findRepo
)

rem Define the relative path to your executable within the repository
set "repoPath=Bench_Repo\IMU_VI"

rem Combine the base directory and the repository path
set "fullPath=%baseDir%\%repoPath%\IMU_COM25Ver2.exe"

rem Start the executable using the full path
start "" "%fullPath%"

endlocal