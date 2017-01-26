from PIL import Image


o1 = Image.open('temp/img00401.bmp')
o2 = Image.open('temp/img02060.bmp')


s1 = set(o1.getdata())
s2 = set(o2.getdata())


print len(s1 & s2) == len(s1)