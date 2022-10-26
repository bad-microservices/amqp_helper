Examples
=================

Here are some examples on how to use :code:`amqp_helper` with some AMQP libraries

aio-pika
---------

.. code-block:: python

    import asyncio
    from amqp_helper import AMQPConfig
    from aio_pika import connect_robust

    amqp_config = AMQPConfig(username="test",password="testpw",vhost="testvhost")

    async def main():

        connection = await connect_robust(**amqp_config.aio_pika())

        # do some amqp stuff

    if __name__ == "__main__":
        asyncio.run(main())