from PySide6.QtWidgets import QApplication, QPushButton

def on_click():
    print("Pressed!")

app = QApplication([])
btn = QPushButton("Click Me")
btn.clicked.connect(on_click)     # signal/slot binding
btn.show()
app.exec()
