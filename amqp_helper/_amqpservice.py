import asyncio
import aio_pika
import uuid
import json
import time

import logging

from typing import MutableMapping, Callable
from aio_pika import Message, connect_robust
from aio_pika.abc import (
    AbstractChannel,
    AbstractConnection,
    AbstractIncomingMessage,
    AbstractQueue,
    DeliveryMode,
)


from amqp_helper import AMQPConfig
from amqp_helper import AMQPFunction


class AMQPService:

    DLX_NAME = "rpc.dlx"

    connection: AbstractConnection
    channel: AbstractChannel
    loop: asyncio.AbstractEventLoop
    queues: MutableMapping[str, AbstractQueue]

    tasks: MutableMapping[str, asyncio.Task]

    def __init__(self, eventloop: asyncio.AbstractEventLoop = None):
        self.functions: MutableMapping[str, Callable] = {}
        self.loop = eventloop or asyncio.get_running_loop()
        self.tasks = {}
        self.queues = {}

    async def connect(self, amqp_config: AMQPConfig) -> "AMQPService":
        self.connection = await connect_robust(**amqp_config.aio_pika(), timeout=5)
        self.channel = await self.connection.channel()

        return self

    async def register_function(self, func: AMQPFunction, **kwargs):

        arguments = kwargs.pop("arguments", {})
        arguments.update({"x-dead-letter-exchange": self.DLX_NAME})
        kwargs["arguments"] = arguments

        queue = await self.channel.declare_queue(func.name, auto_delete=True, **kwargs)
        self.queues[func.name] = queue
        task = self.loop.create_task(self.__handle_msg(func))

        self.tasks[func.name] = task

    async def __handle_msg(self, func: AMQPFunction):
        async with self.queues[func.name].iterator() as qiterator:
            message: AbstractIncomingMessage
            async for message in qiterator:
                try:
                    args = json.loads(message.body) or {}
                    if asyncio.iscoroutinefunction(func.__call__):
                        payload = await func(**args)
                    else:
                        payload = func(**args)

                    print(payload)

                # if we get an json error we are rejecting it without requeing it
                except json.decoder.JSONDecodeError:
                    await message.reject(False)

                #catch errors which did not get catched by the amqfunction
                except Exception as exc:
                    logging.exception(exc)
                    await message.reject(False)
                    continue

                await message.ack()

                # if we should not reply we hop to the next iteration
                if not message.reply_to:
                    continue
                try:
                    result_message = Message(
                        json.dumps(payload).encode(),
                        content_type="application/json",
                        correlation_id=message.correlation_id,
                        delivery_mode=DeliveryMode.NOT_PERSISTENT,
                        timestamp=time.time(),
                        type="result",
                    )
                    await self.channel.default_exchange.publish(
                        result_message,
                        message.reply_to,
                        mandatory=False,
                    )
                except Exception:
                    logging.exception("Failed to send reply %r", result_message)
                    await message.reject(requeue=False)

        self.tasks[func.name].set_result()

    async def serve(self):
        await asyncio.sleep(5)
        tasks_alive = True
        while tasks_alive:
            await asyncio.sleep(1)
            for queue in self.queues.values():
                try:
                    await queue.declare()
                except Exception as exc:
                    print(exc)
                    tasks_alive = False
