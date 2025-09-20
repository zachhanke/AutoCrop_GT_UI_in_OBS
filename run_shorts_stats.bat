@echo off

echo Running Shorts Stats...

python live_shorts_score.py --password <your_obs_password> --source "Golden Tee" --interval .25 --check_x 286 --check_y 125 --check_color 5d1520 --color_tolerance 25 --subcheck_x 1471 --subcheck_y 920 --subcheck_color f10016

if errorlevel 1 exit /b 1