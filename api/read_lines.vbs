Set fso = CreateObject("Scripting.FileSystemObject")
Set file = fso.OpenTextFile("C:\Users\86138\Desktop\thisisfinal\CodeAgent\api\temp_extract\project_20251119_134538_571467_1f92395f\flask-2.0.0\src\flask\cli.py", 1)
lineNum = 1
Do Until file.AtEndOfStream
    line = file.ReadLine
    If lineNum >= 820 And lineNum <= 830 Then
        WScript.Echo lineNum & ": " & line
    End If
    lineNum = lineNum + 1
    If lineNum > 830 Then Exit Do
Loop
file.Close
