import os

os.system(r'cx_Freeze-3.0.1\FreezePython.exe ../giraffe/grafit.pyw --target-dir=dist/grafit')

template = open('grafit.wxst', 'rb')
output = open('grafit.wxs', 'wb')

for line in template:
    if line.strip() == r"<File Id='HelperDLL' Name='Helper.dll' DiskId='1' src='Helper.dll' Vital='yes' />":
        print '!!!'
    else:
        output.write(line)

