#!/usr/bin/env python3

import copy
import sys
import re
import xml.etree.ElementTree as ET
import datetime

version = "1.0"
# set/list of events to ignore (only used for calculating end times)
ignore_events = ['break', 'lunchbreak', 'coffeebreak', 'closing']

# It is rather simple luckily … otherwise it would be smarter to use a proper
# dom model or so.
talk_re = re.compile(r'''
<div\s*class="paper">[\s\r\n]*
<h3>(?P<title>.*?)</h3>[\s\r\n]*
<p\s*class="summary">(?P<summary>.*?)</p>[\r\n\s]*
.*?
<th>Author:</th>[\r\n\s]*
<td>(?P<author>.*?)</td>.*?
<th>Co-presenters:</th>[\r\n\s]*
<td>(?P<coauthors>.*?)</td>.*?
</div>
''', re.VERBOSE|re.MULTILINE|re.DOTALL|re.IGNORECASE)

datetimeformat = '%Y-%m-%dT%H:%M:%S%z'
tzinfo = datetime.timezone(datetime.timedelta(hours=2))


infile = open(sys.argv[1]).read()

events = []

for talk in talk_re.finditer(infile):
    title = talk.group('title').strip()
    summary = talk.group('summary').strip()

    author = talk.group('author').strip()
    coauthors = talk.group('coauthors').strip()

    authors = [author, ]

    if coauthors != 'none':
        for auth in coauthors.split(', '):
            authors.append(auth.strip())

    authors = [re.match('^(?P<name>[^&]*)(&lt;.*&gt;)?', author).group('name').strip() for author in authors]

    event = {}
    event['title'] = title
    event['persons'] = authors
    event['abstract'] = summary
    # Assume english language for everything
    event['language'] = 'eng'
    event['description'] = None
    event['logo'] = None
    event['type'] = 'lecture' # meeting
    event['attachments'] = None
    event['links'] = None
    event['track'] = None
    event['room'] = None
    event['date'] = None
    event['duration'] = None
    event['slug'] = None # Unique identifier for URL?
    event['id'] = None
    event['recording'] = { 'license' : 'CC BY-SA 4.0', 'opt_out' : 'false' }

    events.append(event)


events.append({
    'title' : 'GNOME Foundation Annual General Meeting',
    'abstract' : 'The Annual General Meeting of the GNOME Foundation and team reports.',
    'persons' : ['GNOME Board',],
    'language' : 'eng',
    'type' : 'meeting',
})

events.append({
    'title' : 'Intern Lightning Talks',
    'abstract' : 'Blub.',
    'persons' : ['GSoC and Outreachy Interns',],
    'language' : 'eng',
    'type' : 'lecture',
})


events.append({
    'title' : 'Unconference #1',
    'matchby' : 'Unconference #1',
    'abstract' : 'Yet to be announced',
    'persons' : [],
    'language' : 'eng',
    'type' : 'lecture',
})

events.append({
    'title' : 'Unconference #2',
    'matchby' : 'Unconference #2',
    'abstract' : 'Yet to be announced',
    'persons' : [],
    'language' : 'eng',
    'type' : 'lecture',
})

events.append({
    'title' : 'Unconference #3',
    'matchby' : 'Unconference #3',
    'abstract' : 'Yet to be announced',
    'persons' : [],
    'language' : 'eng',
    'type' : 'lecture',
})

events.append({
    'title' : 'Unconference #4',
    'matchby' : 'Unconference #4',
    'abstract' : 'Yet to be announced',
    'persons' : [],
    'language' : 'eng',
    'type' : 'lecture',
})

events.append({
    'title' : 'Unconference #5',
    'matchby' : 'Unconference #5',
    'abstract' : 'Yet to be announced',
    'persons' : [],
    'language' : 'eng',
    'type' : 'lecture',
})

events.append({
    'title' : 'Unconference #6',
    'matchby' : 'Unconference #6',
    'abstract' : 'Yet to be announced',
    'persons' : [],
    'language' : 'eng',
    'type' : 'lecture',
})

events.append({
    'title' : 'Keynote 1',
    'matchby' : 'Keynote 1',
    'abstract' : 'Yet to be announced',
    'persons' : [],
    'language' : 'eng',
    'type' : 'lecture',
})

events.append({
    'title' : 'Keynote 2',
    'matchby' : 'Keynote 2',
    'abstract' : 'Yet to be announced',
    'persons' : [],
    'language' : 'eng',
    'type' : 'lecture',
})

######################################

title_list = [event['title'] for event in events]

title_list.sort()

f = open('titles.txt', 'w')
f.write('\n'.join(title_list))

# Ensure it is written in case schedule.xml creation fails
f.close()


######################################

def find_event(title):
    for event in events:
        if ('matchby' in event and event['matchby'].lower() == title.lower()) or  event['title'].lower() == title.lower():
            # Assume it is the same
            return event
    raise AssertionError('Event %s could not be found!' % title)


lines = open(sys.argv[2]).readlines()
rooml = lines.pop(0)
rooms = []
for room in rooml.split('\t'):
    room = room.strip()
    if not room:
        continue

    rooms.append(room)


slot_day = 0
slot_events = []
slot_start = None

for l in lines:
    if not l.strip():
        continue
    try:
        l = l.split('\t')
        if l[0]:
            day = int(l[0])

        if not l[1]:
             continue

        start_time = l[1].strip()
        new_slot_events = [ i.strip() for i in l[2:] ]
    except:
        pass

    for event in new_slot_events:
        if event.lower() in ignore_events:
            new_slot_events = []

    slot_end = start_time

    # Do the closing of the previous events
    for i, event in enumerate(slot_events):
        if not event:
            continue

        event = find_event(event)

        event['start'] = slot_start
        event['end'] = slot_end
        event['day'] = day
        event['room'] = rooms[i]


    # For next iteration
    slot_events = new_slot_events
    slot_start = slot_end




#####################################

schedule = ET.Element('schedule')
ET.SubElement(schedule, 'version').text = version

event_ignored_tags = {'id', 'matchby', 'end'}

conference = {
  'days' : 4,
  'title' : 'GUADEC 2016',
  'start' : '2016-07-12',
  'end' : '2016-08-14',
  'acronym' : 'GUADEC2016',
  'timeslot_duration' : '00:15', # What does this mean?
}

def add_elements(et, elements, ignore=set()):
    for key, val in elements.items():
        if key in event_ignored_tags:
            continue

        if isinstance(val, dict):
            el = ET.SubElement(et, key)
            add_elements(el, val)
        elif isinstance(val, list):
            el = ET.SubElement(et, key)

            tagname = key[:-1]
            for item in val:
                ET.SubElement(el, tagname).text = item
        elif val is None:
            ET.SubElement(et, key)
        else:
            ET.SubElement(et, key).text = str(val)

add_elements(ET.SubElement(schedule, 'conference'), conference)

for dayid in range(1, conference['days']):
    day = ET.SubElement(schedule, 'day')
    day.attrib['index'] = str(dayid)
    date = datetime.datetime.strptime(conference['start'], '%Y-%m-%d')
    date = date.date() + datetime.timedelta(days=dayid - 1)
    day.attrib['date'] = date.strftime('%Y-%m-%d')

    day_start = None
    day_end = None

    for roomname in rooms:
        room = ET.SubElement(day, 'room')
        room.attrib['name'] = roomname

        for event in events:
            if not 'room' in event or event['room'] != roomname or event['day'] != dayid:
                continue

            start = event['start']
            end = event['end']

            start = datetime.datetime(*date.timetuple()[:3], *[int(i) for i in start.split(':')], tzinfo=tzinfo)
            end = datetime.datetime(*date.timetuple()[:3],  *[int(i) for i in end.split(':')], tzinfo=tzinfo)

            if day_start is None:
                day_start = start
            if start < day_start:
                day_start = start

            if day_end is None:
                day_end = end
            if end > day_end:
                day_end = end


            duration = end - start
            dseconds = duration.total_seconds()

            event['date'] = start.strftime(datetimeformat)
            event['duration'] = "%02i:%02i" % (dseconds // (60 * 60), dseconds // (60) % 60)

            ev = ET.SubElement(room, 'event')
            add_elements(ev, event, event_ignored_tags)

    if day_start:
        day.attrib['start'] = day_start.strftime(datetimeformat)
        day.attrib['end'] = day_end.strftime(datetimeformat)

open('schedule.xml', 'bw').write(ET.tostring(schedule, encoding='UTF-8'))

