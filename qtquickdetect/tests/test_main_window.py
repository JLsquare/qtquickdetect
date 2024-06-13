import pytest
from qtquickdetect.views.main_window import MainWindow


@pytest.fixture
def app(qtbot):
    main_window = MainWindow()
    qtbot.addWidget(main_window)
    return main_window


def test_window_title(app):
    assert app.windowTitle() == "QTQuickDetect"


def test_initial_state_of_window(app):
    assert app.size().width() == 1524
    assert app.size().height() == 720
