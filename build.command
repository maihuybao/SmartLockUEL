# Build onefile — chi bundle ui/ va images/ vao exe
# datasets/ nam ben ngoai, canh file exe

# macOS:
pyinstaller --onefile \
  --name "SmartLockerUEL" \
  --windowed \
  --icon images/UEL_Logo.icns \
  --add-data "ui:ui" \
  --add-data "images:images" \
  --add-data "datasets/language.json:datasets" \
  --distpath dist/macOS \
  --noconfirm \
  main.py

# Windows:
pyinstaller --onefile --name "SmartLockerUEL" --windowed --icon images/UEL_Logo.ico --add-data "ui:ui" --add-data "images:images" --add-data "datasets/language.json:datasets" --distpath dist/Windows --noconfirm main.py