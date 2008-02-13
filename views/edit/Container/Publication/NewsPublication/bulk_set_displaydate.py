##parameters=objects
# set the display_date_time
now = DateTime()
for obj in objects:
    if hasattr(obj, 'implements_newsitem') and obj.implements_newsitem():
        unapproved = obj.get_unapproved_version()
        if unapproved is None:
            continue
        unapproved = getattr(obj, unapproved)
        if unapproved.display_datetime() is None:
            unapproved.set_display_datetime(now)

