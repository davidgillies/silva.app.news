from threading import Thread

class TimeoutWrapper:
    """Used to run a certain method with a timeout.

    Usage:

    t = TimeoutWrapper(<method>, <args>, <kwargs>)
    success = t.run_with_timeout(<timeout>)
    if success:
        retval = t.return_value()
    else:
        raise Exception, 'Operation timed out'

    When calling the 'run_with_timeout' method, <method> is called with
    arguments <args> and keyword arguments <kwargs>. If the method succeeds 
    within the requested time, 1 is returned, and the result of the call can 
    be retrieved using the 'return_value' method. If this process takes 
    longer then <timeout> (seconds), 0 is returned by the 'run_with_timeout' 
    method (and 'return_value' returns None).
    """
    
    def __init__(self, handler, args=(), kwargs={}):
        """Initializes the object.
        
        Arguments are:
        
        - handler: a reference to the method to be called
        - args: a list of non-keyword arguments that should be passed to the 
                method
        - kwargs: a dict of keyword arguments that should be passed to the 
                method
        """
        self._handler = handler
        self._args = args
        self._kwargs = kwargs
        self._success = 0
        self._retval = None

    def run_with_timeout(self, timeout):
        """Class the method

        Arguments are:
        
        - timeout: an integer (or float) specifying the timeout in seconds
        """
        thread = Thread(target=self._run_thread)
        thread.start()
        thread.join(timeout)
        del thread
        return self._success

    def return_value(self):
        """Returns the return value of the method (if any)

        No arguments required.
        """
        return self._retval

    def _run_thread(self):
        """Internal method that actually calls the method.

        Will set self._retval and self._success if successful.
        """
        self._retval = self._handler(*self._args, **self._kwargs)
        self._success = 1
        
