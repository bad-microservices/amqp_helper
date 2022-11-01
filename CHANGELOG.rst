Changelog
===========

0.0.4
-------
* AMQPLogHandler should now properly close down on SIGINT of parent task

0.0.3
-------
* on import will print a warning if aio-pika is missing because the AMQPLogHandler needs it

0.0.2
------
* added the AMQPLogHandler

0.0.1
-------
Initial version supporting :code:`aio-pika`