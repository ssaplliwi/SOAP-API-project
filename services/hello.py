from spyne import ServiceBase, rpc, Unicode

class HelloService(ServiceBase):
    @rpc(Unicode, _returns=Unicode)
    def say_hello(ctx, name):
        return f"Hello, {name}!"
