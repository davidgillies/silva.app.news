##parameters=model

editable = model.get_editable()

if editable is None:
    viewable = model.get_viewable()
    approved = model.get_approved_version()
    if viewable is not None:
        return None
    last_closed = model.get_last_closed()
    if last_closed is None:
        # probably this case never occurs as there's always
        # at least a last_closed version if there's no editable and
        # no viewable version
        return None
    return last_closed.display_datetime()
return editable.display_datetime()



