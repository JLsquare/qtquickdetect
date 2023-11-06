from PyQt6.QtWidgets import QApplication
from views.start_view import StartView

# Set up the QApplication
app = QApplication([])

# Show the main window
window = StartView()
window.show()

# Run the application
app.exec()