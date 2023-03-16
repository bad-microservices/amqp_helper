import asyncio
from typing import Callable, MutableMapping

class AMQPFunction:
    name: str
    func: Callable
    exception_handlers: MutableMapping[Exception,Callable]

    def __init__(self,func_name:str,func:Callable):
        self.name = func_name
        self.func = func
        self.exception_handlers = {}
        
    def exception_handler(self,*args,**kwargs):
        def method_wrapper(wrapped_function):
            for exc in args:
                self.exception_handlers[exc] = wrapped_function
            return wrapped_function
        return method_wrapper

def new_amqp_func(func_name:str,func:Callable):
    if asyncio.iscoroutinefunction(func):
        return AsyncAQMPFunction(func_name,func)
    return SyncAQMPFunction(func_name,func)

class SyncAQMPFunction(AMQPFunction):
    def __call__(self,*args,**kwargs):
        try:
            return self.func(*args,**kwargs)
        except Exception as exc:
            for exc_type in self.exception_handlers.keys():
                if isinstance(exc,exc_type):
                    return self.exception_handlers[exc_type](*args,exc=exc,**kwargs)
            raise exc

class AsyncAQMPFunction(AMQPFunction):
    async def __call__(self,*args,**kwargs):
        try:
            return await self.func(*args,**kwargs)
        except Exception as exc:
            for exc_type in self.exception_handlers.keys():
                if isinstance(exc,exc_type):
                    return await self.exception_handlers[exc_type](*args,exc=exc,**kwargs)
            raise exc