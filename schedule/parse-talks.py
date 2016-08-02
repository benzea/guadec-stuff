#!/usr/bin/env python3

import copy
import sys
import re
import xml.etree.ElementTree as ET
import datetime
import html

elsewhere_room = "Elsewhere"
elsewhere_type = ""

version = "1.0"
# set/list of events to ignore (only used for calculating end times)
ignore_events = ['END']

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
<td>(?P<coauthors>.*?)[\r\n\s]*(<form.*?form>)?[\r\n\s]*</td>.*?
<th>Talk\ length:</th>[\r\n\s]*
<td>(?P<length>.*?)</td>.*?
<th>Status:</th>[\r\n\s]*
<td>(?P<status>.*?)</td>.*?
</div>
''', re.VERBOSE|re.MULTILINE|re.DOTALL|re.IGNORECASE)

tzinfo = datetime.timezone(datetime.timedelta(hours=2))


infile = open(sys.argv[1]).read()

events = []
eventid = 1

for talk in talk_re.finditer(infile):
    title = html.unescape(talk.group('title').strip())
    summary = html.unescape(talk.group('summary').strip())

    author = html.unescape(talk.group('author').strip())
    coauthors = html.unescape(talk.group('coauthors').strip())

    status = html.unescape(talk.group('status').strip())
    length = html.unescape(talk.group('length').strip())

    authors = [author, ]

    if coauthors != 'none':
        for auth in coauthors.split(', '):
            authors.append(auth.strip())

    authors = [re.match('^(?P<name>[^<]*)(<.*>)?', author).group('name').strip() for author in authors]

    # This is a bit weird, but one title contains a ... replace it to … as
    # libreoffice insists to change it
    title = title.replace('...', '…')

    event = {}
    event['title'] = title
    event['subtitle'] = None
    event['persons'] = authors
    event['abstract'] = summary
    # Assume english language for everything
    event['language'] = 'eng'
    event['description'] = None
    event['logo'] = None
    event['type'] = 'talk'
    event['attachments'] = None
    event['links'] = None
    event['track'] = None
    event['room'] = None
    event['date'] = None
    event['duration'] = None
    event['slug'] = None # Unique identifier for URL?
    event['id'] = eventid
    event['recording'] = { 'license' : 'CC BY-SA 4.0', 'optout' : 'false' }

    event['_status'] = status
    event['_length'] = length

    eventid += 1

    events.append(event)

# Make sure the these manual events do not change their ID (at least once
# we feed the data into the streaming website and such)
eventid = 100

events.append({
    'title' : 'GNOME Foundation Annual General Meeting',
    'matchby' : 'agm',
    'subtitle' : None,
    'logo' : None,
    'track' : None,
    'links' : None,
    'attachments' : None,
    'abstract' : 'The Annual General Meeting of the GNOME Foundation and team reports.',
    'persons' : ['GNOME Board',],
    'language' : 'eng',
    'type' : 'meeting',
    'recording': { 'license' : 'CC BY-SA 4.0', 'optout' : 'false' },
   'id' : eventid,
})
eventid += 1

events.append({
    'title' : 'Intern lightning talks',
    'subtitle' : None,
    'logo' : None,
    'track' : None,
    'links' : None,
    'attachments' : None,
    'abstract' : 'Lightning talks of Google Summer of Code and Outreachy interns',
    'persons' : ['GSoC and Outreachy Interns',],
    'language' : 'eng',
    'recording': { 'license' : 'CC BY-SA 4.0', 'optout' : 'false' },
    'type' : 'talk',
    'id' : eventid,
})
eventid += 1

events.append({
    'title' : 'Lightning talks',
    'subtitle' : None,
    'logo' : None,
    'track' : None,
    'links' : None,
    'attachments' : None,
    'abstract' : 'Lightning talks',
    'persons' : [],
    'language' : 'eng',
    'recording': { 'license' : 'CC BY-SA 4.0', 'optout' : 'false' },
    'type' : 'talk',
    'id' : eventid,
})
eventid += 1

events.append({
    'title' : 'Unconference #1',
    'subtitle' : None,
    'logo' : None,
    'track' : None,
    'links' : None,
    'attachments' : None,
    'matchby' : 'Unconference #1',
    'abstract' : 'Yet to be announced',
    'persons' : ['to be announced'],
    'language' : 'eng',
    'recording': { 'license' : 'CC BY-SA 4.0', 'optout' : 'false' },
    'type' : 'talk',
    'id' : eventid,
    'slug' : '%i-unconference-1' % eventid,
})
eventid += 1

events.append({
    'title' : 'Unconference #2',
    'subtitle' : None,
    'logo' : None,
    'track' : None,
    'links' : None,
    'attachments' : None,
    'matchby' : 'Unconference #2',
    'abstract' : 'Yet to be announced',
    'persons' : ['to be announced'],
    'language' : 'eng',
    'recording': { 'license' : 'CC BY-SA 4.0', 'optout' : 'false' },
    'type' : 'talk',
    'id' : eventid,
    'slug' : '%i-unconference-2' % eventid,
})
eventid += 1

events.append({
    'title' : 'Unconference #3',
    'subtitle' : None,
    'logo' : None,
    'track' : None,
    'links' : None,
    'attachments' : None,
    'matchby' : 'Unconference #3',
    'abstract' : 'Yet to be announced',
    'persons' : ['to be announced'],
    'language' : 'eng',
    'recording': { 'license' : 'CC BY-SA 4.0', 'optout' : 'false' },
    'type' : 'talk',
    'id' : eventid,
    'slug' : '%i-unconference-3' % eventid,
})
eventid += 1

events.append({
    'title' : 'Unconference #4',
    'subtitle' : None,
    'logo' : None,
    'track' : None,
    'links' : None,
    'attachments' : None,
    'matchby' : 'Unconference #4',
    'abstract' : 'Yet to be announced',
    'persons' : ['to be announced'],
    'language' : 'eng',
    'recording': { 'license' : 'CC BY-SA 4.0', 'optout' : 'false' },
    'type' : 'talk',
    'id' : eventid,
    'slug' : '%i-unconference-4' % eventid,
})
eventid += 1

events.append({
    'title' : 'Unconference #5',
    'subtitle' : None,
    'logo' : None,
    'track' : None,
    'links' : None,
    'attachments' : None,
    'matchby' : 'Unconference #5',
    'abstract' : 'Yet to be announced',
    'persons' : ['to be announced'],
    'language' : 'eng',
    'recording': { 'license' : 'CC BY-SA 4.0', 'optout' : 'false' },
    'type' : 'talk',
    'id' : eventid,
    'slug' : '%i-unconference-5' % eventid,
})
eventid += 1

events.append({
    'title' : 'Unconference #6',
    'subtitle' : None,
    'logo' : None,
    'track' : None,
    'links' : None,
    'attachments' : None,
    'matchby' : 'Unconference #6',
    'abstract' : 'Yet to be announced',
    'persons' : ['to be announced'],
    'language' : 'eng',
    'recording': { 'license' : 'CC BY-SA 4.0', 'optout' : 'false' },
    'type' : 'talk',
    'id' : eventid,
    'slug' : '%i-unconference-6' % eventid,
})
eventid += 1

events.append({
    'title' : "Confessions of a command line geek: Why I don't use GNOME but everyone else should",
    'subtitle' : None,
    'logo' : None,
    'track' : None,
    'links' : None,
    'attachments' : None,
    'matchby' : 'Keynote 1',
    'abstract' : '''Despite what tablet- and phone-loving pundits say, the laptop is here to stay. When a user wants to watch a movie on a train, they reach for the tablet first. But if they want to do actual, real work, they still prefer the laptop.

Meanwhile, software freedom should always be for everyone, not just technical users and software developers. The GNOME project was one of the first in this history of Free Software to realize this, and seek to create a free software desktop that truly allowed everyone to enjoy the software freedom that those of us had already happily found with Bash and Emacs (or vi :) years before.

This keynote will discuss why GNOME remains best poised to deliver software freedom to everyone, how GNOME continues to be the best welcome-mat for those who want software freedom, and why GNOME remains absolutely essential to the advancement of software freedom for decades to come.''',
    'persons' : ['Bradley Kuhn'],
    'recording': { 'license' : 'CC BY-SA 4.0', 'optout' : 'false' },
    'language' : 'eng',
    'type' : 'talk',
    'id' : eventid,
})
eventid += 1

events.append({
    'title' : 'We want more centralization, do we?',
    'subtitle' : None,
    'logo' : None,
    'track' : None,
    'links' : None,
    'attachments' : None,
    'matchby' : 'Keynote 2',
    'abstract' : '''The roots of the Internet can be found in the move from large mainframes to smaller and locally connected machines (Unices or VAXen) Unix. Obviously there was a need to connect to remote machines in a convenient way and not only with manually managed uucp networks.

Eventually in the mid 90ies decentralization was achieved and directly visible due to Gopher and the Web. With the move of the big search engines to a general service providers, things started to revert to the former centralization.

The Internet still looks like a collection of many computers but in reality most system do not anymore work without access to, say, apis.google.com. Unfortunately desktops environments moved in the same direction.
Do we really want to rely on other peoples machines?''',
    'persons' : ['Werner Koch'],
    'recording': { 'license' : 'CC BY-SA 4.0', 'optout' : 'false' },
    'language' : 'eng',
    'type' : 'talk',
    'id' : eventid,
})
eventid += 1

events.append({
    'title' : 'Opening',
    'subtitle' : None,
    'logo' : None,
    'track' : None,
    'links' : None,
    'attachments' : None,
    'matchby' : 'opening',
    'abstract' : '',
    'persons' : ['GUADEC Team'],
    'recording': { 'license' : 'CC BY-SA 4.0', 'optout' : 'false' },
    'language' : 'eng',
    'type' : 'talk',
    'id' : eventid,
})
eventid += 1


events.append({
    'title' : 'Closing',
    'subtitle' : None,
    'logo' : None,
    'track' : None,
    'links' : None,
    'attachments' : None,
    'matchby' : 'closing',
    'abstract' : '',
    'persons' : ['GUADEC Team'],
    'recording': { 'license' : 'CC BY-SA 4.0', 'optout' : 'false' },
    'language' : 'eng',
    'type' : 'talk',
    'id' : eventid,
})
eventid += 1

events.append({
    'title' : 'BBQ at AKK',
    'subtitle' : None,
    'logo' : None,
    'track' : None,
    'links' : None,
    'attachments' : None,
    'abstract' : 'Pre-registration meeting in the AKK beer garden (on campus) and BBQ there. We will provide food, drinks are inexpensive but not free. Bring cash for payment.',
    'persons' : ['AKK and GUADEC Teams'],
    'recording': { 'license' : 'no-video', 'optout' : 'true' },
    'language' : 'eng',
    'type' : '',
    'id' : eventid,
})
eventid += 1

events.append({
    'title' : 'Picnic',
    'subtitle' : None,
    'logo' : None,
    'track' : None,
    'links' : None,
    'attachments' : None,
    'abstract' : 'We are going to go to a park and picnic there. Some games, light food, and drinks will be provided.',
    'persons' : ['GUADEC Team'],
    'recording': { 'license' : 'no-video', 'optout' : 'true' },
    'language' : 'eng',
    'type' : '',
    'id' : eventid,
})
eventid += 1

events.append({
    'title' : 'Z10',
    'subtitle' : None,
    'logo' : None,
    'track' : None,
    'links' : None,
    'attachments' : None,
    'abstract' : 'Bar evening at Z10. There will be no food available.',
    'persons' : ['Z10 and GUADEC Teams'],
    'recording': { 'license' : 'no-video', 'optout' : 'true' },
    'language' : 'eng',
    'type' : '',
    'id' : eventid,
})
eventid += 1

events.append({
    'title' : 'Centricular Dinner at Hoepfener Burg',
    'matchby' : 'Hoepfener Burg',
    'subtitle' : None,
    'logo' : None,
    'track' : None,
    'links' : None,
    'attachments' : None,
    'abstract' : 'We are going to visit the beer garden at the Hoepfener Burg (local brewery) and have a sponsored dinner there.',
    'persons' : [],
    'recording': { 'license' : 'no-video', 'optout' : 'true' },
    'language' : 'eng',
    'type' : '',
    'id' : eventid,
})
eventid += 1


# All events in room "Elsewhere" are auto generated
eventid = 200


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
        if '_auto' in event:
            continue
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

slots = []

for l in lines:
    if not l.strip():
        continue
    l = l.split('\t')
    if l[0]:
        day_new = int(l[0])
        if slot_day != day_new:
            slot_start = None

            for e in slot_events:
                assert(not e)

            slot_day = day_new

    if not l[1]:
         continue

    start_time = l[1].strip()
    new_slot_events = [ i.strip() for i in l[2:] ]

    for event in new_slot_events:
        if event.lower() in ignore_events:
            new_slot_events = []

    slot_end = start_time

    slot_filled = False
    for ev in slot_events:
        if ev:
            slot_filled = True
    if slot_filled:
        slots.append([slot_day, slot_start, slot_end])

    # Do the closing of the previous events
    for i, event in enumerate(slot_events):
        if not event:
            continue

        try:
            event = find_event(event)
        except:
            event = {
                'title' : event,
                'room' : rooms[i],
                'subtitle' : None,
                'logo' : None,
                'track' : None,
                'links' : None,
                'attachments' : None,
                'abstract' : None,
                'persons' : [],
                'recording': { 'license' : 'no-video', 'optout' : 'true' },
                'language' : 'eng',
                'type' : elsewhere_type,
                'id' : eventid,
                '_auto' : True,
            }
            eventid += 1
            events.append(event)

        event['start'] = slot_start
        event['end'] = slot_end
        event['day'] = slot_day
        event['room'] = rooms[i]


    # For next iteration
    slot_events = new_slot_events
    slot_start = slot_end




#####################################

schedule = ET.Element('schedule')
ET.SubElement(schedule, 'version').text = version

event_ignored_tags = {'id', 'matchby', 'end', 'day', 'placed' }
event_ensure_tags = { 'logo', 'description', 'recording', 'track', 'links', 'attachments' }

conference = {
  'days' : 4,
  'title' : 'GUADEC 2016',
  'start' : '2016-08-11',
  'end' : '2016-08-14',
  'acronym' : 'GUADEC2016',
  'timeslot_duration' : '00:15', # What does this mean?
}

def add_elements(et, elements, ignore=set()):
    for key, val in elements.items():
        if key in event_ignored_tags:
            continue

        if key.startswith('_'):
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

for dayid in range(1, conference['days'] + 1):
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

            event['placed'] = True

            if not 'slug' in event or event['slug'] is None:
                title = event['title']
                # Try to keep the slug the same even if title changes (for unconference mostly)
                if 'matchby' in event:
                    title = event['matchby']
                event['slug'] = "%i-%s" % (event['id'], re.subn(r'[^a-zA-Z_ 0-9]', '', event['title'].lower())[0].strip().replace(' ', '_'))

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

            if '_length' in event:
                if 'Short' in event['_length']:
                    assert(dseconds == 30*60)
                if 'Long' in event['_length']:
                    assert(dseconds == 45*60)


            event['date'] = start.isoformat()
            event['duration'] = "%02i:%02i" % (dseconds // (60 * 60), dseconds // (60) % 60)

            ev = ET.SubElement(room, 'event')
            ev.attrib['id'] = str(event['id'])
            add_elements(ev, event, event_ignored_tags)

    if day_start:
        day.attrib['start'] = day_start.isoformat()
        day.attrib['end'] = day_end.isoformat()

open('schedule.xml', 'bw').write(ET.tostring(schedule, encoding='UTF-8'))


###

html = ET.Element('div')
html.attrib['class'] = "schedule"


abstracts = {}

for dayid in range(1, conference['days'] + 1):
    tmp = ET.SubElement(html, 'h3')

    date = datetime.datetime.strptime(conference['start'], '%Y-%m-%d')
    date = date.date() + datetime.timedelta(days=dayid - 1)

    tmp.text = date.strftime('%A %d. %B %Y')

    table = ET.SubElement(html, 'table')
    thead = ET.SubElement(table, 'thead')

    # Header
    tr = ET.SubElement(thead, 'tr')
    td = ET.SubElement(tr, 'td')
    td.text = ""

    for room in rooms[:2]:
        td = ET.SubElement(tr, 'td')
        td.text = room

    tbody = ET.SubElement(table, 'tbody')

    for slot in slots:
        slot_day, slot_start, slot_end = slot
        if slot_day != dayid:
            continue

        tr = ET.SubElement(tbody, 'tr')
        td = ET.SubElement(tr, 'td')
        td.text = slot_start

        td_rooms = []
        td_rooms.append(ET.SubElement(tr, 'td'))
        td_rooms.append(ET.SubElement(tr, 'td'))

        # Insert a row underneath if the next slot is not adjacent to this one.
        try:
            next_slot = slots[slots.index(slot)+1]
            if next_slot[0] == slot_day and next_slot[1] != slot_end:
                tr_extra = ET.SubElement(tbody, 'tr')
                td = ET.SubElement(tr_extra, 'td')
                td.text = slot_end
                ET.SubElement(tr_extra, 'td')
                ET.SubElement(tr_extra, 'td')
        except IndexError:
            pass

        for event in sorted(events, key=lambda x: x['room'] if 'room' in x and x['room'] else ''):
            if 'room' not in event or 'day' not in event or event['day'] != dayid or event['start'] != slot_start:
                continue

            try:
                td = td_rooms[rooms.index(event['room'])]
            except IndexError:
                # Replace with a colspan
                colspan = len(td_rooms)
                for td in td_rooms[1:]:
                    tr.remove(td)
                td = td_rooms[0]
                td.attrib['colspan'] = str(colspan)


            if 'abstract' in event and event['abstract']:
                div = ET.Element('div')
                div.attrib['class'] = 'abstract'
                div.attrib['id'] = 'abstract-' + event['slug']

                header = ET.SubElement(div, 'h4')
                a = ET.SubElement(header, 'a')
                a.text = event['title']
                a.attrib['href'] = '#' + event['slug']

                details = ET.SubElement(div, 'span')
                details.attrib['class'] = 'details'
                details.text = 'On ' + date.strftime('%A') + ' at ' + event['start'] + ' (' + event['room'] + ')'
                if event['persons']:
                    details.text += ' by ' + ', '.join(event['persons'])

                abstract = event['abstract'].split('\n\n')
                for paragraph in abstract:
                    p = ET.SubElement(div, 'p')
                    first = True
                    for line in paragraph.split('\n'):
                        if not first:
                            br = ET.SubElement(p, 'br')
                            br.tail = line
                        else:
                            first = False
                            p.text = line

                #div.text = event['abstract']
                abstracts[event['title']] = div


            td.attrib['class'] = 'talk'
            td.attrib['id'] = event['slug']

            header = ET.SubElement(td, 'span')
            header.attrib['style'] = 'font-weight: bold'

            if 'abstract' in event and event['abstract']:
                hdrtext = ET.SubElement(header, 'a')
                hdrtext.attrib['href'] = '#abstract-' + event['slug']
            else:
                hdrtext = header

            hdrtext.text = event['title']

            if event['persons']:
                br = ET.SubElement(td, 'br')
                br.tail = ', '.join(event['persons'])


tmp = ET.SubElement(html, 'h3')
tmp.text = 'Abstracts'

for title in sorted(abstracts):
    html.append(abstracts[title])





tree = ET.ElementTree(html)
tree.write('schedule.html', encoding='UTF-8', xml_declaration=False)


#####





unplaced = set()
for event in events:
    if 'placed' in event and event['placed']:
        continue
    if '_status' in event and 'confirmed' not in event['_status']:
        continue
    unplaced.add(event['title'])

if unplaced:
    print('Not all events were placed in the schedule!')
    for title in sorted(unplaced):
        print(' * %s' % title)

