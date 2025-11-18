from ui.app import SeeDoApp
from controller.controller import AppController
from core.secrets import load_secrets


if __name__ == "__main__":
    controller = AppController()
    app = SeeDoApp(controller)
    app.mainloop()
