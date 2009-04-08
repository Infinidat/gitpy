def quote_for_shell(s):
    """
    >>> print quote_for_shell('this is a " string')
    "this is a \\" string"
    >>> print quote_for_shell('this is a $shell variable')
    "this is a \\$shell variable"
    >>> print quote_for_shell(r'an escaped \\$')
    "an escaped \\\\\\$"
    """
    returned = s.replace("\\", "\\\\").replace('"', '\\"').replace("$", "\\$")
    if " " in returned:
        returned = '"%s"' % returned
    return returned
    
if __name__ == '__main__':
    import doctest
    doctest.testmod()
