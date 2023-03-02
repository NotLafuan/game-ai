@echo off
cls
echo python setup.py build
python setup.py build
del utilsModule.cp310-win_amd64.pyd
copy build\lib.win-amd64-cpython-310\utilsModule.cp310-win_amd64.pyd utilsModule.cp310-win_amd64.pyd
rmdir /s /q build
echo ------------------
echo python test.py
python test.py