def x_to_string(val):
    try: #literally, ask the func to try and apply certain func. if impossible-doesn't return error, but an exception
        return eval(val)
    except TypeError:
        return val #returns value if previous attempt(eval) didn't work
