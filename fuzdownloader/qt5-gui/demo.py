import sys

from PyQt5.QtCore import Qt, QTranslator, QLocale
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication
from qframelesswindow import FramelessWindow, StandardTitleBar, AcrylicWindow
from qfluentwidgets import setThemeColor, FluentTranslator, setTheme, Theme, SplitTitleBar
# from Ui_LoginWindow import Ui_Form
from LoginWindow import Ui_Form


class LoginWindow(AcrylicWindow, Ui_Form):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # setTheme(Theme.DARK)
        setThemeColor('#28afe9')

        self.setTitleBar(SplitTitleBar(self))
        self.titleBar.raise_()

        # self.label.setScaledContents(False)
        # self.setWindowTitle('PyQt-Fluent-Widget-login')
        self.setWindowIcon(QIcon(":/images/icon.png"))
        self.resize(1000, 650)

        # self.windowEffect.setMicaEffect(self.winId(), isDarkMode=False)
        self.windowEffect.setMicaEffect(self.winId())
        self.setStyleSheet("LoginWindow{background: rgba(235, 235, 235, 1.0)}")
        self.titleBar.titleLabel.setStyleSheet("""
            QLabel{
                background: transparent;
                font: 13px 'Segoe UI';
                padding: 0 4px;
                color: white
            }
        """)

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        # pixmap = QPixmap(":/images/background.jpg").scaled(
            # self.label.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        # self.label.setPixmap(pixmap)


def run_qt5_gui():
    # enable dpi scale
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)

    # Internationalization
    translator = FluentTranslator(QLocale())
    app.installTranslator(translator)

    w = LoginWindow()
    w.show()
    app.exec_()