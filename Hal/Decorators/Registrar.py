from inspect import isfunction

from docstring_parser import parse

from Event_Handler import event_handler


def makeRegistrar():
    registry = {}

    def outer(name, funcIdentifier=None):
        # if the function should be init and returned when registrar is called ex @reg() or @reg(name="ex name")
        def registrar(func, funcIdentifier=funcIdentifier, name=name):
            # add functions that are not called to the registry the reason it is done in the inner function here is becasuae if it is done outside then it does not have access to the fucntion name unless it is said explicitly
            try:
                funcIdentifier = funcIdentifier or func.__name__
                skill = func.__qualname__.split(".")[0]
                identifier = f"{skill}-{funcIdentifier}"
                docstring = parse(func.__doc__)
                description = (
                    docstring.short_description or "" + docstring.long_description or ""
                )
            except Exception as e:
                event_handler.trigger("Error", e)
            else:
                registry[identifier.lower()] = {
                    "id": identifier.lower(),
                    "name": name.lower(),
                    "function": func,
                    "description": description,
                    "docstring": docstring,
                    "skill": skill,
                    "func_name_in_class": func.__name__,
                    "simple_func_ref": func,
                }

            return func

        return registrar

    outer.all = registry
    return outer


reg = makeRegistrar()
