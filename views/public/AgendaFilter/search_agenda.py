## Script (Python) "search_agenda"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=month, year
##title=
##
months = context.get_months()
monthnumber = int(months.index(month) + 1)

year = int(year)

startdate = DateTime(year, monthnumber, 1)
enddate = None

if monthnumber == 12:
    enddate = DateTime(year + 1, 1, 1)
else:
    enddate = DateTime(year, monthnumber + 1, 1)

query = {}
query['start_datetime'] = [startdate, enddate]
query['start_datetime_usage'] = 'range:min:max'

query['meta_type'] = ['Silva EUR Event', 'Silva EUR Oration', 'Silva EUR Promotion', 'Silva EUR ValedictoryLecture']

result = context.nieuws_search(query)

return result or []
