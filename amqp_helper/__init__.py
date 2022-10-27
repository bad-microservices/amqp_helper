"""A Helper Library to configure AMQP Connections.

This Module contains the :code:`AMQPConfig` Class which can be helpfull to connect to AMQP Brokers.

Todo:
    * add support for pika
    * add more configurable options

"""


from ._version import __version__
from ._amqpconfig import AMQPConfig
from ._amqploghandler import AMQPLogHandler

__all__ = ["__version__","AMQPConfig","AMQPLogHandler"]