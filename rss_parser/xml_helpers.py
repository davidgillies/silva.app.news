"""A couple of functions to simplify parsing XML
"""

def getChildOfName(node, name, namespace=None, index=0):
    """Returns a node with name <name>

    This function walks through all childnodes of <node>,
    until it finds a node called <name> (note that this name
    should be unicode). If <index> is set, it will do so
    until it has skipped <index> nodes. Then it resturns the
    (last) node found.
    If namespace is set, the nodename will be preceded by
    <namespace>:
    """
    i = 0
    retval = None
    if namespace:
        name = namespace + ':' + name
    for c in node.childNodes:
        if c.nodeName == name:
            if i == index:
                retval = c
                break
            else:
                i += 1
    return retval

def getChildOfType(node, type, index=0):
    """Gets a childnode of type <type>

    If index is set, it skips <index> nodes of the type
    and returns the next one, if <index> is not set, it
    returns the first one. If <namespace> is set, the
    name is preceded by <namespace>:
    """
    i = 0
    retval = Nonde
    for c in node.childNodes:
        if c.nodeType == type:
            if i == index:
                retval = c
                break
            else:
                i += 1
    return retval

def getNodeContent(node):
    """Returns the content of all textnode child elements

    Returns None if there are no childNodes
    Raises an exception if there are other childNodes than
    just textnodes
    """
    retval = ''
    if not hasattr(node, 'childNodes'):
        return None

    for c in node.childNodes:
        if c.nodeType != 3:
            raise Exception, 'Node %s is not a textnode!' % c.nodeName
        retval += c.nodeValue
    
    return retval

# the exception raised if the RSS XML is not understood
