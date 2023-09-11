import os
import json
import signal
import atexit
import asyncio
import aio_pika
import traceback
import multiprocessing as mp

from queue import Empty
from datetime import datetime, timedelta
from logging import StreamHandler, LogRecord
from typing import Optional

from amqp_helper._amqpconfig import AMQPConfig



class AMQPLogHandler(StreamHandler):
    def __init__(self, amqp_config: AMQPConfig, exchange_name: Optional[str] = "amq.topic"):
        StreamHandler.__init__(self)
        self.msg_queue = mp.Queue()
        self.stopping = mp.Event()
        self.logprocess = LogProcess(
            self.msg_queue, amqp_config, self.stopping, exchange_name
        )
        self.logprocess.daemon = False
        self.logprocess.start()
        atexit.register(self.stopping.set)

    def emit(self, record):
        self.msg_queue.put_nowait(_logrecord_to_dict(record))


class LogProcess(mp.Process):
    loop = None

    def __init__(
        self,
        queue: mp.Queue,
        amqp_config: AMQPConfig,
        event: mp.Event,
        exchange_name: str,
    ):
        super(LogProcess, self).__init__()
        self.mpqueue = queue
        self.cfg = amqp_config
        self.parent_stopping = event
        self.exchange_name = exchange_name

    @property
    def parent_alive(self):
        stop_flag_set = self.parent_stopping.is_set()
        pid_changed = self._parent_pid != os.getppid()
        if pid_changed:
            print("parent process pid changed!")
        return not (stop_flag_set or pid_changed)

    def run(self):
        self.loop = asyncio.new_event_loop()
        self.asqueue = asyncio.Queue()

        try:
            self.loop.run_until_complete(self.main())
        finally:
            self.loop.stop()

        # kill this process because somehow any other way does not work?
        os.kill(os.getpid(), signal.SIGKILL)

    async def main(self):
        self.connection = await aio_pika.connect_robust(**self.cfg.aio_pika())
        l = await asyncio.gather(
            self.handle_asqueue(), self.get_from_mp_queue(), loop=self.loop
        )

    async def handle_asqueue(self):
        connection = self.connection

        channel = await connection.channel()
        exchange = await channel.declare_exchange(self.exchange_name,aio_pika.ExchangeType.TOPIC,durable=True)

        while self.parent_alive:
            try:
                msg = self.asqueue.get_nowait()
            except asyncio.QueueEmpty:
                await asyncio.sleep(0.1)
                continue

            routing_key = f"{msg['logger']}.{msg['level']}"
            await exchange.publish(
                aio_pika.Message(
                    body=json.dumps(msg).encode("utf-8"),
                    content_encoding="utf-8",
                    content_type="text/json",
                    expiration=datetime.now()
                    + timedelta(seconds=self.cfg.message_lifetime),
                ),
                routing_key=routing_key,
            )

        await connection.close()

    async def get_from_mp_queue(self):
        running = True
        while running:
            try:
                msg = await asyncio.to_thread(self.mpqueue.get, timeout=2)
                await self.asqueue.put(msg)
            except Empty:
                if not self.parent_alive:
                    running = False


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
