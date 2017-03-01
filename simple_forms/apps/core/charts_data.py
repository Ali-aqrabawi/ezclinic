# charset: utf-8

from calendar import monthrange
from itertools import groupby, takewhile, dropwhile
import datetime as dt
import json
import logging


def year_range(day=None):
    """Return first day of month 11 months before
    and last day of month of today"""
    if day is None:
        day = dt.date.today()
    days = monthrange(day.year, day.month)[1]
    end_of_month = day.replace(day=days)
    year_ago = day.replace(year=(day.year - 1), day=1)
    return year_ago, end_of_month

def months_iterator(start, stop=None):
    current = start.replace(day=1)
    stop_m = stop.replace(day=1) if stop else None
    while True:
        if stop_m and current == stop_m:
            return
        yield current
        current = (current + dt.timedelta(days=33)).replace(day=1)

def appointments_count(records, start, stop):
    """Return appointments count by month from start to stop inclusively.
    Month without appointments counts as zero"""
    dates = dict((key, len(list(appointments)))
                 for key, appointments
                 in groupby(records, lambda d: (d.year, d.month)))

    pretty_dates = []
    for m in months_iterator(start, stop + dt.timedelta(days=2)):
        pretty_dates.append((m.strftime("%b %Y"),
                             dates.get((m.year, m.month), 0)))

    return pretty_dates


def appointments(records, start=None, stop=None):
    if not start:
        start, stop = year_range()

    dates = appointments_count(records, start, stop)

    return json.dumps({
        "chart": {
            "type": "column",
            },
        "title": {
            "text": "Appointments",
            },
        "xAxis": {
            "categories": [month for month, _ in dates],
            "crosshair": True
            },
        "yAxis": {
            "title": {
                "text": "Count"
                }
            },
        "series": [{
            "name": "Months",
            "data": [{"name": month, "y": count}
                for month, count in dates]
            }]
        }, indent=2)

