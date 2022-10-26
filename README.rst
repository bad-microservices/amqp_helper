================
amqp_helper
================

Introduction
=============

:code:`amqp_helper` aims to be a simple Helper library to configure AMQP communication via other librarys like :code:`aio-pika` or :code:`pika`.
To achieve this goal this Library provides the :code:`AMQPConfig` class which enables us to configure the connection Parameters for other librarys in a unified way.

Installation
==============

:code:`amqp_helper` can be installed in multiple ways. The easiest Solution is to install it with :code:`pip`.

via pip
---------

.. code-block:: bash

    python3 -m pip install amqp-helper


from source
------------

.. code-block:: bash

    git clone https://github.com/bad-microservices/amqp_helper.git
    cd amqp_helper
    python3 -m pip install .

Example (aio-pika)
===================

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