pause
@echo off
echo =======================================================
echo StLouis311 - Automated Processing of 311 (Civil Service Requests) JSON Data to Geodatabase
echo For more info about the raw data, visit: https://www.stlouis-mo.gov/data/datasets/dataset.cfm?id=5
echo =======================================================

set arcpropy="C:\Program Files\ArcGIS\Pro\bin\Python\Scripts\propy.bat"

set SCRIPT_DIR=%~dp0

rem call the main.py script to run the processing
echo Running the main processing script...
if not exist "%SCRIPT_DIR%main.py" (
    echo Error: main.py not found in the script directory.
    pause
    exit /b 1
)
%arcpropy% "%SCRIPT_DIR%main.py"

pause
echo Processing complete. The data has been updated in the geodatabase. 
echo You can now open the StLouis311.gdb in ArcGIS Pro to view the updated data.

pause



