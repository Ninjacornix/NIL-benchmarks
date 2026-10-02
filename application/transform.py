import sys
with open(sys.argv[1], 'rb') as source:
    data = bytearray(source.read())
for index in range(len(data)):
    data[index] = 255 - data[index]
with open(sys.argv[2], 'wb') as output:
    output.write(data)
print(len(data))
