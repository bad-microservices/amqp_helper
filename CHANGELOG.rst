Changelog
===========

0.1.7
------
* **BUGFIX**
   * :code:`AMQPLogHandler` use :code:`os.kill` again because :code:`self.kill` had some problems
   * :code:`AMQPClient.call` now cancels the Future and uses a Timeout for the response as well. 

0.1.6
------
* **BUGFIX**
   * :code:`AMQPLogHandler` Serialisation of :code:`exc_info` did not check if it was :code:`None`

0.1.5
------
* :code:`AMQPClient.call` now has a timeout set by default.
* :code:`AMQPLogHandler` should now behave better
* minor Type Hint clean up

0.1.4
------
* **BUGFIX**
   * :code:`AMQPLogHandler` :code:`asyncio.gather` was called with loop parameter which is not available in python 3.11+

0.1.3
------
* **BUGFIX**
   * :code:`AMQPLogHandler` Log Task created :code:`asyncio.Queue` with loop parameter which is not available in python 3.11+

0.1.2
------
* :code:`AMQPConfig.aio_pika()` ssl_options is now returning :code:`cafile` instead of :code:`ca_certs`
* **BREAKING**:
   * :code:`aio_pika` is now required

0.1.1
------
* **BUGFIX**:
   * :code:`LogProcess.handle_asqueue()` uses :code:`self.asqueue.get()` which could get stuck

0.1.0
------
* :code:`AMQPLogHandler` takes optional Argument
* **IMPORTANT**: The Exchange gets declared everytime so make sure the config stays the same
* **BREAKING**:
   * :code:`AMQPLogHandler` got reworked to use a topic exchange
   * it will only log everything which got transferred to the log process while the parent process was running

0.0.13
------
* :code:`AMQPClient` has new Function :code:`close()` to close the AMQP connection
* :code:`AMQPLogHandler` got reworked to work without throwing an error
   * it will only log everything which got transferred to the log process while the parent process was running

0.0.12
------
* :code:`AMQPService.serve()` had a 'memory leak'. Now it does not Recreate :code:`Queues` instead it redeclares the old ones.

0.0.11
------
* :code:`AMQPFunction` Exception handlers now get the Exception which occured passed as keyword argument :code:`exc`

0.0.10
------
* :code:`AMQPService` should now no longer crash if an :code:`AMQPFunction` Exception is not catched.
* :code:`AMQPFunction` Excpetion Handlers now use isinstance instead of an exact class match
   * :code:`Exception` should now catch all Exceptions
   * NOTE: The priority of handling is the same order as the handlers were added. That means if you added an handler for :code:`Exception` first it will catch all errors.

0.0.9
------
* added :code:`AMQPFunction`
   * a wrapper around a function
   * Exception handlers can be attached to it
   * should be used in conjunction with the :code:`AMQPService`
* added :code:`AMQPService`
   * a class for creating AMQP Services
   * allows calling functions over amqp with a seperate queue for each function
* added :code:`AMQPClient`
   * a simple rpc client inspired by the tutorial from the aio_pika documentation

Mind that the new Features are still WIP!

0.0.8
------
* bugfix -> regression fixed readded log_ prefix

0.0.7
------
* bugfix for ssl_options since it was not defined

0.0.6
-------
* dont create the SSL Context manualy
* instead pass relevant Info as Argument 
  
0.0.5
-------
* added :code:`log_` to queue names so we dont run into the weird issue that RabbitMQ can't openn the error log 

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
* Initial version supporting :code:`aio-pika`