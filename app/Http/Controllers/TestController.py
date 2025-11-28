from app.Http.Controllers.Controller import Controller

class TestController(Controller):
    def index(self, request):
        return self.view("test", request)
