"""A Helper Library to configure AMQP Connections.

This Module contains the :code:`AMQPConfig` Class which can be helpfull to connect to AMQP Brokers.

Todo:
    * add support for pika
    * add more configurable options

"""
import ssl

from dataclasses import dataclass
from typing import Optional

from ._version import __version__

@dataclass
class AMQPConfig:
    """Config class for AMQP Connections

    Attributes:
        host (str, optional): Host or IP of the AMQP Server. Defaults to :code:`"localhost"`
        port (int, optional): Port to use. Defaults to :code:`5672`.
        username (str, optional): Username used for connecting to the AMQP Server. Defaults to :code:`"guest"`.
        password (str, optional): Password used for connecting to the AMQP Server. Defaults to :code:`"guest"`.
        vhost (str, optional): Vhost which we want to connect to. Defaults to :code:`"/"`.
        connection_name (str, optional): Name to register the connection with. Defaults to :code:`None`.
        ca_file (str, optional): If you want to use an SSLContext for connecting specify the path to the ca File here. Defaults to :code:`None`.
        
    """
    host:str = "localhost"
    port:int = 5672
    username:str="guest"
    password:str="guest"
    vhost:str="/"
    connection_name:Optional[str] = None
    ca_file: Optional[str] = None


    @property
    def ssl(self):
        """bool: :code:`True` if you specified an :code:`ca_file`."""
        return self.ca_file is not None

    @property
    def ssl_context(self):
        """ssl.SSLContext | None: if you specified an :code:`ca_file` will return an :code:`SSLContext`. If not it will return :code:`None`."""
        if self.ca_file is None:
            return None
        return ssl.create_default_context(cafile=self.ca_file)
    
    @property
    def client_properties(self):
        if self.connection_name is None:
            return None
        return {"name":self.connection_name}

    def aio_pika(self) -> dict:
        """This Function is used to create a dictionary which can be passed to aio-pika

        Returns:
            dict: Dictionary which you can pass to aio-pika.connect_robust
        """
        return {
            "host":self.host,
            "port": self.port,
            "login": self.username,
            "password": self.password,
            "virtualhost": self.vhost,
            "client_properties": self.client_properties,
            "ssl":self.ssl,
            "ssl_context": self.ssl_context
        }


__all__ = ["__version__","AMQPConfig"]