# This file was cleaned of null bytes by Copilot.
with open('gulfofmexico/ide/app.py', 'rb') as f:
    data = f.read()
clean = data.replace(b'\x00', b'')
with open('gulfofmexico/ide/app.py', 'wb') as f:
    f.write(clean)
print('Null bytes removed from app.py')
