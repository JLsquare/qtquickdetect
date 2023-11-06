import logging
from PyQt6.QtWidgets import QApplication
from views.start_view import StartView

# Configure logging
log_format = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)

# Set up the QApplication
app = QApplication([])

# Show the main window
window = StartView()
window.show()

# Run the application
app.exec()