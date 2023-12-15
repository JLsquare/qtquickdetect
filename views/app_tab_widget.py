from typing import Optional
from PyQt6.QtWidgets import QTabWidget, QWidget, QTabBar
from views.new_project_window import NewProjectWindow


class AppTabWidget(QTabWidget):
    def __init__(self):
        super().__init__()

        # PyQT6 Components
        self._new_project_window: Optional[NewProjectWindow] = None

        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)
        self.tabBarClicked.connect(self.check_tab)
        self.addTab(QWidget(), "+")
        self.tabBar().setTabButton(self.count() - 1, QTabBar.ButtonPosition.RightSide, None)

    ##############################
    #         CONTROLLER         #
    ##############################

    def check_tab(self, index: int):
        if index == self.count() - 1:
            self.add_new_tab()

    def add_new_tab(self, new_tab: QWidget = None, title: str = "Start", redirect: bool = True) -> None:
        if new_tab is None:
            self._new_project_window = NewProjectWindow(self.add_new_tab)
            self._new_project_window.show()
            return
        self.insertTab(self.count() - 1, new_tab, title)
        if redirect:
            self.setCurrentIndex(self.count() - 2)
        if self.count() == 1:
            self.addTab(QWidget(), "+")
            self.tabBar().setTabButton(self.count() - 1, QTabBar.ButtonPosition.RightSide, None)

    def close_tab(self, index: int):
        if self.count() > 1:
            if hasattr(self.widget(index), 'stop'):
                self.widget(index).stop()
            self.removeTab(index)
            self.setCurrentIndex(self.count() - 2)
