@echo off
call C:\Users\Gabriel\Anaconda3\Scripts\activate.bat C:\Users\Gabriel\Anaconda3

set start=-s 0 -d 20

:loop 
if [%1]==[] goto :done
set start=%start% -i %1
shift
goto :loop

:done
python "C:\Users\Gabriel\Documents\Python Scripts\CalciumImagingHelpers\TIFreview.py" %start%