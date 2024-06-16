import pytest
from qtquickdetect.views.about_widget import AboutWidget
from qtquickdetect.views.main_window import MainWindow
from PyQt6 import QtCore

from qtquickdetect.views.models_widget import ModelsWidget
from qtquickdetect.views.presets_widget import PresetsWidget
from qtquickdetect.views.collections_widget import CollectionsWidget
from qtquickdetect.views.app_config_widget import AppConfigWidget
from qtquickdetect.views.inference_widget import InferenceWidget
from qtquickdetect.views.inference_stream_widget import InferenceStreamWidget
from qtquickdetect.views.inference_history_widget import InferenceHistoryWidget




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

def test_switch_tabs(app, qtbot):
    """
    Tries to switch between sidebar tabs and checks if the correct widget is displayed.
    """
    WIDGET_LIST = {
        1: ModelsWidget,
        2: PresetsWidget,
        3: (CollectionsWidget, 'image'),
        4: (CollectionsWidget, 'video'),
        5: (InferenceWidget, 'image'),
        6: (InferenceWidget, 'video'),
        7: InferenceStreamWidget,
        8: InferenceHistoryWidget,
        9: AppConfigWidget,
        10: AboutWidget
    }

    def click_on_tab(tab_index):
        elem = app._side_menu.item(tab_index)
        rect = app._side_menu.visualItemRect(elem)
        qtbot.mouseClick(app._side_menu.viewport(), QtCore.Qt.MouseButton.LeftButton, pos=rect.center())

    def is_right_widget_shown(index):
        widget = WIDGET_LIST[index]
        if isinstance(widget, tuple):
            expected = widget[0]
            media_type = widget[1]

            assert isinstance(app._content_stack.currentWidget(), expected), f"Expected {expected}, got {app._content_stack.currentWidget()}"
            assert app._content_stack.currentWidget().media_type == media_type
        else:
            assert isinstance(app._content_stack.currentWidget(), widget), f"Expected {widget}, got {app._content_stack.currentWidget()}"


    for tab_index, widget in WIDGET_LIST.items():
        click_on_tab(tab_index)
 
        is_right_widget_shown(tab_index)

  
