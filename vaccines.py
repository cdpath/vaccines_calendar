import csv
import sys
from collections import namedtuple
from datetime import date, timedelta

from dateutil import parser
from dateutil.relativedelta import relativedelta
from ics import Calendar, Event
from ics.alarm import DisplayAlarm


def load_csv(fname):
    with open(fname) as f:
        f_csv = csv.reader(f)
        headings = next(f_csv)
        headings = parse_headings(headings)
        Row = namedtuple('Row', headings)
        return [Row(*r) for r in f_csv]


def parse_headings(hs):
    for idx, h in enumerate(hs):
        if h == '名称':
            hs[idx] = 'name'
        elif h == '缩写':
            hs[idx] = 'abbv'
        elif h == '出生时':
            hs[idx] = 'M0'
        elif '月' in h:
            hs[idx] = 'M' + h[:-1]
        elif '岁' in h:
            hs[idx] = 'M' + str(int(h[:-1]) * 12)
    return hs


def create_ics(birthday=None, add_alarms=False, schedule_file='./vaccines.csv', ical_file='./vaccines.ics'):
    if birthday is None:
        birthday = date.today()
    else:
        birthday = parser.parse(birthday)

    c = Calendar()
    for v in load_csv(schedule_file):
        v = v._asdict()
        target_months = [k for k, v_ in v.items() if k.startswith('M') and v_]
        total = v[target_months[-1]]
        for month in target_months:
            name = v['name'] + f' {v[month]}/{total}'
            begin = birthday + relativedelta(months=int(month[1:]))
            if add_alarms:
                alarms = [DisplayAlarm(trigger=timedelta(hours = 1))]
            else:
                alarms = None
            e = Event(name=name, begin=begin, description=v['abbv'], alarms=alarms)
            e.make_all_day()
            c.events.add(e)
    with open(ical_file, 'w') as f:
        f.writelines(c)


if __name__ == '__main__':
    birthday = sys.argv[1]
    create_ics(birthday)
