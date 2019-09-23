cls
@echo off
call C:\Users\stoeltig\AppData\Local\Continuum\anaconda3\Scripts\activate.bat C:\Users\stoeltig\AppData\Local\Continuum\anaconda3\
set start=-b 2

:loop 
set "start=%start% -i %1"
shift
if [%1]==[] goto :done
goto :loop

:done

python D:\Gabriel\Python\CalciumImagingHelpers\ReduceConcat.py %start%
pause