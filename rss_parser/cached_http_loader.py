from httplib import HTTPConnection
from urlparse import urlparse

from file_like_object import *
from timeout_wrapper import *

class HTTPException(Exception):
    """Raised if a status code different then 200 or 304 is returned
    """

class TimeoutException(Exception):
    """Raised if the request times out
    """

class CachedHTTPLoader:
    """Downloads a URL, but first sees if it should use its cache
    """
    
    # we use a global cache, so it is shared between different instances
    _cache = {}

    def urlopen(self, url):
        last_etag = None
        last_modified = None

        scheme, netloc, path, parameters, query, fragment = urlparse(url)

        host = netloc
        port = None
        if netloc.find(':') > -1:
            host, port = netloc.split(':')
            port = int(port)
            
        if query:
            path += '?%s' % query
            
        # check if we have a cached version of the url's response and if so,
        # grab that
        cached = None
        if self._cache.has_key(url):
            cached = self._cache[url]
            last_etag = cached['etag']
            last_modified = cached['last-modified']

        # use either ETag or Last-Modified header to see if we need to use 
        # cached or new version
        headers = {}
        if last_etag:
            headers['If-None-Match'] = last_etag
        elif last_modified:
            headers['If-Modified-Since'] = last_modified
        
        # now send the request and fetch the result
        if not port:
            h = HTTPConnection(host)
        else:
            h = HTTPConnection(host, port)
        
        # make the request
        t = TimeoutWrapper(h.request, ('GET', path), {'headers': headers})
        # for now set the timeout to 30 seconds
        if not t.run_with_timeout(30):
            raise TimeoutException, 'The request to %s timed out' % host

        # now fetch result
        r = h.getresponse()

        # see if we have to use cached
        retval = {}
        wascached = 0
        if r.status == 304:
            # use cached data
            data = cached['data']
            wascached = 1
        elif r.status == 200:
            # return returned data and add info to cache
            data = r.read()
            cached = {}
            cached['etag'] = None
            cached['last-modified'] = None
            last_etag = None
            last_modified = None
            if r.msg.has_key('etag'):
                cached['etag'] = r.msg['etag']
                last_etag = r.msg['etag']
            if r.msg.has_key('last-modified'):
                cached['last-modified'] = r.msg['last-modified']
                last_modified = r.msg['last-modified']
            cached['data'] = data
            self._cache[url] = cached
        else:
            raise HTTPException, 'Errorcode %s returned from the server' % r.status

        retval = FileLikeObject()
        retval.write(data)
        
        # add a attribute to the return value so we can see whether 
        # the response is cached
        retval.wascached = wascached
        retval.etag = last_etag
        retval.last_modified = last_modified
        retval.info = lambda: r.msg
        # urllib also follows redirects, and the following method is only
        # useful if that happened, but to become somewhat compatible, we
        # add the method anyway
        retval.geturl = lambda: url
        
        return retval 
        
