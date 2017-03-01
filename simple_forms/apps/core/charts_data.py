# coding: utf-8

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
    """Iterate by month starting with start month.
    If stop is not None, then iterate until reaching
    stop month not including it

    Returns first day of month
    """
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
        # Fill gaps with zeroes
        pretty_dates.append((m.strftime("%b %Y"),
                             dates.get((m.year, m.month), 0)))

    return pretty_dates


def appointments(records, start=None, stop=None):
    if not start:
        start, stop = year_range()

    dates = appointments_count(records, start, stop)

    return json.dumps({
        "chart": {"type": "column"},
        "title": {"text": "Appointments" },
        "xAxis": {
            "categories": [month for month, _ in dates],
            "crosshair": True
            },
        "yAxis": {"title": {"text": "Count"}},
        "series": [{
            "name": "Appointments",
            "data": [{"name": month, "y": count}
                     for month, count in dates]
            }]
        }, indent=2)

def revenue_cumulative_sums(records, start, stop):
    month_receipts = groupby(records, lambda r: (r.created_at.year,
                                                 r.created_at.month))
    month_receipts = dict((month, sum(r.amount for r in group))
                          for month, group in month_receipts)

    s = 0
    cumulative_sums = []
    for m in months_iterator(start, stop + dt.timedelta(days=2)):
        # Fill gaps with zeroes
        s += month_receipts.get((m.year, m.month), 0)
        cumulative_sums.append((m.strftime("%b %Y"), float(s)))

    return cumulative_sums

def revenue(records, start=None, stop=None):
    """Cumulative revenue amounts by months"""
    if not start:
        start, stop = year_range()

    cumulative_sums = revenue_cumulative_sums(records, start, stop)

    return json.dumps({
        "title": {"text": "Revenue"},
        "xAxis": {
            "categories": [month for month, _ in cumulative_sums]},
        "yAxis": {"title": {"text": "Amount"}},
        "series": [{
            "name": "Revenue",
            "data": [{"name": month, "y": value}
                     for month, value in cumulative_sums]
            }]
        }, indent=2)

def pie_chart(title, data):
    return {"chart": {
                "plotBackgroundColor": None,
                "plotBorderWidth": None,
                "plotShadow": False,
                "type": "pie",
                },
            "title": {
                "text": title,
                },
            "tooltip": {
                "pointFormat": "{series.name}: <b>{point.y} — {point.percentage:.1f}%</b>"
                },
            "plotOptions": {
                "pie": {
                    "allowPointSelect": True,
                    "cursor": "pointer",
                    "dataLabels": {"enabled": False},
                    "showInLegend": True
                    }},
                "series": [{
                    "name": title,
                    "colorByPoint": True,
                    "data": data
                    }]
                }

def dental_charts(records):
    d_c = {"extraction": 0, "filling": 0, "rct": 0}
    for extraction, filling, rct in records:
        d_c["extraction"] += extraction
        d_c["filling"] += filling
        d_c["rct"] += rct

    return json.dumps(
            pie_chart("Dental charts",
            [{"name": "extraction", "y": d_c["extraction"], "color": "#4D6790"},
             {"name": "filling", "y": d_c["filling"], "color": "#FF8400"},
             {"name": "rct", "y": d_c["rct"], "color": "#91CEB0"}]))


def ages(records):
    # We have 5 groups for ages sliced by 10, and the last group is for
    # all ages greather than 40
    groups = [0] * 5
    for key, group in groupby(sorted(person.age for person in records),
                              lambda age: age // 10):
        if key > 4:
            groups[4] += len(list(group))
        else:
            groups[key] = len(list(group))
    return json.dumps(
            pie_chart("Patients Ages Chart",
                      [{"name": name, "y": count}
                       for name, count in
                       zip(["<10", "10—19", "20—29", "30—40", "40"], groups)]))
