import asyncio
import json
import aio_pika
import os
import multiprocessing
import time
import sys


from datetime import datetime, timedelta
import traceback
from logging import StreamHandler, LogRecord


asyncio.Queue
from ._amqpconfig import AMQPConfig

def amqplogprocess(queue:multiprocessing.Queue):
    loop = asyncio.get_event_loop() 

    async def main():
        futu = loop.run_in_executor(None,queue.get())
        futu.add_done_callback(callback)

    async def callback():

        pass
    while not queue.empty():
        
    try:
        loop.run_until_complete()
    finally:
        loop.close()

class AMQPLogHandler(StreamHandler):
    def __init__(self, amqp_config: AMQPConfig):
        StreamHandler.__init__(self)
        self.msg_queue = multiprocessing.Queue(0)
        self.worker = AMQPWorker(amqp_config, os.getpid())
        self.start_worker_process()

    def start_worker_process(self):
        self.process = multiprocessing.Process(
            target=self.worker.start,
            args=[self.msg_queue],
        )
        # self.process.daemon = True
        self.process.start()
        print("started worker process")

    def emit(self, record):
        if not self.process.is_alive():
            self.start_worker_process()
        self.msg_queue.put_nowait(_logrecord_to_dict(record))


class AMQPWorker:
    amqp_config: AMQPConfig
    parent_pid: int

    def __init__(self, amqp_config: AMQPConfig, parent_pid: int):
        self.amqp_config = amqp_config
        self.parent_pid = parent_pid

    @property
    def parent_alive(self):
        print(os.getppid())
        print(self.parent_pid)
        return os.getppid() == self.parent_pid 

    async def do_work(self, queue: multiprocessing.Queue):
        print(f"ASYNC PID {os.getpid()}")
        print("got told to do work!")
        connection = await aio_pika.connect_robust(**self.amqp_config.aio_pika())
        async with connection:
            channel = await connection.channel()
            while self.parent_alive:
                while queue.qsize > 0:
                    msg = queue.get()
                    routing_key = msg["level"]
                    await channel.default_exchange.publish(
                        aio_pika.Message(
                            body=json.dumps(msg).encode("utf-8"),
                            content_encoding="utf-8",
                            content_type="text/json",
                            expiration=datetime.now()
                            + timedelta(self.amqp_config.message_lifetime),
                        ),
                        routing_key=routing_key,
                    )
                    

    def start(self, queue):
        print(f"PARENTPID {self.parent_pid}")
        print(f"OS:GETPPID {os.getppid()}")
        print(f"CHILD PID {os.getpid()}")
        #loop = asyncio.get_event_loop()
        #loop.run_until_complete(self.do_work(queue))
        asyncio.run(self.do_work(queue))


def _logrecord_to_dict(obj: LogRecord) -> dict:
    exc_time = datetime.fromtimestamp(obj.created)
    new_dict = {
        "level": str(obj.levelname),
        "msg": str(obj.msg),
        "args": str(obj.args),
        "logger": str(obj.name),
        "file": str(obj.filename),
        "module": str(obj.module),
        "line_number": str(obj.lineno),
        "function_name": str(obj.funcName),
        "timestamp": exc_time.isoformat(),
        "relative_time": str(obj.relativeCreated),
        "pid": str(obj.process),
        "process_name": str(obj.processName),
    }
    try:
        new_dict["exception_info"] = traceback.format_tb(obj.exc_info[2])
    except Exception:
        pass
    return new_dict
