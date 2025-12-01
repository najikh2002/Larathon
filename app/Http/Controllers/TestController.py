from app.Http.Controllers.Controller import Controller

class TestController(Controller):
    def index(self, request):
        return self.view("test", request)

    def coba(self):
        return self.view("coba")
