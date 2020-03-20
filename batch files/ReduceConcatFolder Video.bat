@echo off
call C:\Users\Auswertung\Anaconda3\Scripts\activate.bat C:\Users\Auswertung\Anaconda3

set start=-b 2

:loop 
if [%1]==[] goto done
set start=%start% -i %1
shift
goto :loop

:done
python "D:\Gabriel\Python\CalciumImagingHelpers\ReduceConcatFolderVideo.py" %start%
pause