from ui.app import SeeDoApp
from ui.styles.button_styles import setup_button_styles
from controller.controller import AppController
from core.secrets import load_secrets


if __name__ == "__main__":
    controller = AppController()
    app = SeeDoApp(controller)
    setup_button_styles()
    app.mainloop()

