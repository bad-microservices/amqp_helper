import os
import json
import asyncio
import atexit
import aio_pika
import traceback
import multiprocessing as mp

from queue import Empty

from datetime import datetime, timedelta
from logging import StreamHandler, LogRecord

from ._amqpconfig import AMQPConfig


class AMQPLogHandler(StreamHandler):
    def __init__(self, amqp_config: AMQPConfig):
        StreamHandler.__init__(self)
        self.msg_queue = mp.Queue()
        self.logprocess = LogProcess(self.msg_queue, amqp_config, os.getpid())
        self.logprocess.daemon = True
        self.logprocess.start()
        atexit.register(self.logprocess.set_parent_pid,-1)
        atexit.register(self.msg_queue.close)
        atexit.register(self.logprocess.close)

    def emit(self, record):
        self.msg_queue.put_nowait(_logrecord_to_dict(record))


class LogProcess(mp.Process):
    def __init__(self, queue: mp.Queue, amqp_config: AMQPConfig, parent_pid: int):
        self.queue = queue
        self.cfg = amqp_config
        self.parent_pid = parent_pid
        super().__init__()

    def set_parent_pid(self,new_pid:int):
        self.parent_pid = new_pid

    @property
    def parent_alive(self):
        print(self.parent_pid,os.getppid())
        return self.parent_pid == os.getppid()

    def run(self):
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.log())
        #asyncio.run(self.log())
        print("loghandler closed?")

    def get_message(self) -> dict:

        try:
            msg = self.queue.get_nowait()
            return msg
        except Exception:
            return None

    async def log(self):
        # loop = asyncio.get_event_loop()
        connection = await aio_pika.connect_robust(**self.cfg.aio_pika())
        async with connection:
            channel = await connection.channel()
            while self.parent_alive or not self.queue.empty():
                print(self.parent_alive, not self.queue.empty())
                msg = await asyncio.to_thread(self.get_message)
                if msg is not None:
                    print(f"hello from pid {os.getpid()}")
                    routing_key = msg["level"]
                    print(f"sending msg {msg['msg']} from pid {os.getpid()}")
                    await channel.default_exchange.publish(
                        aio_pika.Message(
                            body=json.dumps(msg).encode("utf-8"),
                            content_encoding="utf-8",
                            content_type="text/json",
                            expiration=datetime.now()
                            + timedelta(seconds=self.cfg.message_lifetime),
                        ),
                        routing_key=routing_key,
                    )


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
