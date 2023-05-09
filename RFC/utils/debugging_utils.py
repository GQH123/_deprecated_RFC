def check_circular_reference(obj, name='Root'):
    attrs = getattr(obj, '__dict__', {})
    print('Checking', repr(name))
    print(attrs, end='\n\n')
    for attr in attrs:
        check_circular_reference(attrs[attr], attr)