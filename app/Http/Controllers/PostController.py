from app.Http.Controllers.Controller import Controller

class PostController(Controller):
    def index(self, request):
        return self.view("postcontroller.index", request)

    def create(self, request):
        return self.view("postcontroller.create", request)

    async def store(self, request):
        return {"message": "Store new PostController"}

    def show(self, request, id):
        return self.view("postcontroller.show", request, {"id": id})

    def edit(self, request, id):
        return self.view("postcontroller.edit", request, {"id": id})

    async def update(self, request, id):
        return {"message": f"Update {id} PostController"}

    def destroy(self, request, id):
        return {"message": f"Delete {id} PostController"}
