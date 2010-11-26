##parameters=model

next_id = model.get_next_version()
if next_id is not None:
    next = getattr(model, next_id)
    return next.display_datetime()
    
viewable = model.get_viewable()
if viewable is not None:
    return None
last_closed = model.get_last_closed()
if last_closed is None:
    # probably this case never occurs as there's always
    # at least a last_closed version if there's no editable and
    # no viewable version
    return None
return last_closed.display_datetime()




