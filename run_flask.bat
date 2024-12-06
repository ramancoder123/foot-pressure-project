@echo off
title Starting Flask Web Application
echo Starting Flask Web Application...

REM Start the Flask app in a minimized window and detach it
start/min cmd /c "python app.py"

REM Open the default browser to the Flask app
start "" "http://127.0.0.1:5000/"

REM Exit the batch file to close the Command Prompt immediately
exit