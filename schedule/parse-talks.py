#!/usr/bin/env python3

import uuid
import copy
import sys
import re
import xml.etree.ElementTree as ET
import datetime
import html

elsewhere_room = "Elsewhere"
elsewhere_type = ""

namespace_uuid = uuid.UUID(hex="d43154ca7d274456a566d48f0aeea991")

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


if len(sys.argv) != 3:
    sys.stderr.write(
        "Usage: %s guadec-talks.html schedule\n" % sys.argv[0])
    sys.exit(1)

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
    'title' : 'GNOME Foundation AGM (part 1)',
    'matchby' : 'GNOME Foundation AGM 1',
    'subtitle' : None,
    'logo' : None,
    'track' : None,
    'links' : None,
    'attachments' : None,
    'abstract' : 'The annual general meeting of the GNOME Foundation: team reports',
    'persons' : ['GNOME Board',],
    'language' : 'eng',
    'type' : 'meeting',
    'recording': { 'license' : 'CC BY-SA 4.0', 'optout' : 'false' },
   'id' : eventid,
})
eventid += 1

events.append({
    'title' : 'GNOME Foundation AGM (part 2)',
    'matchby' : 'GNOME Foundation AGM 2',
    'subtitle' : None,
    'logo' : None,
    'track' : None,
    'links' : None,
    'attachments' : None,
    'abstract' : 'The annual general meeting of the GNOME Foundation: Q&A with the board.',
    'persons' : ['GNOME Board',],
    'language' : 'eng',
    'type' : 'meeting',
    'recording': { 'license' : 'CC BY-SA 4.0', 'optout' : 'false' },
   'id' : eventid,
})
eventid += 1

events.append({
    'title' : 'Interns lightning talks',
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
    'abstract' :
        'Fast-paced and focused talks on any and all subjects. All talks will '
        'be subject to a strict time limit of 5 minutes on stage (including setup). '
        'Slides are welcome, but not compulsory.<br><br>'
        'You will be able to sign up for a lightning talk slot from 11.00AM on '
        'Sunday 29th on a signup sheet at the info desk. Talks will be accepted '
        'on a first come, first serve basis.',
    'persons' : [],
    'language' : 'eng',
    'recording': { 'license' : 'CC BY-SA 4.0', 'optout' : 'false' },
    'type' : 'talk',
    'id' : eventid,
})
eventid += 1

OPEN_TALKS_DESCRIPTION = (
    '20 minute slots for talks and discussion panels to be submitted and '
    'selected by attendees on-site. This is your chance to present cutting '
    'edge developments or anything that did not make it into the normal '
    'schedule.<br><br>'
    'You can propose talks from 11.00, and other attendees will add a '
    'vote to the ones that they would like to see. At 15.30, the talk '
    'with the most votes will be selected and scheduled, so keep an eye '
    'on schedule board!''')

for i in range(1,9):
    events.append({
        'title' : 'Open talk #%i' % i,
        'subtitle' : None,
        'logo' : None,
        'track' : None,
        'links' : None,
        'attachments' : None,
        'matchby' : 'Open talk #%i' % i,
        # WARNING, delete the below when changing the abstract!
        'abstract_title' : 'Open talk',
        'abstract' : OPEN_TALKS_DESCRIPTION,
        'persons' : ['to be announced'],
        'language' : 'eng',
        'recording': { 'license' : 'CC BY-SA 4.0', 'optout' : 'false' },
        'type' : 'talk',
        'id' : eventid,
        'slug' : '%i-unconference-1' % eventid,
    })
    print(events[-1])
    eventid += 1


events.append({
    'title' : "Keynote: The Battle Over Our Technology",
    'subtitle' : None,
    'logo' : None,
    'track' : None,
    'links' : None,
    'attachments' : None,
    'matchby' : 'Keynote 1',
    'abstract' : '''Karen’s keynote will take a broad look at ethics in technology, a topic that is fundamental to many of those involved in GNOME and something that becomes ever more relevant as technology and society develop.''',
    'persons' : ['Karen Sandler'],
    'recording': { 'license' : 'CC BY-SA 4.0', 'optout' : 'false' },
    'language' : 'eng',
    'type' : 'talk',
    'id' : eventid,
})
eventid += 1

events.append({
    'title' : 'Conference opening',
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
    'title' : 'Conference closing',
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
    'title' : 'Pre-registration at Kro Bar',
    'subtitle' : None,
    'logo' : None,
    'track' : None,
    'links' : None,
    'attachments' : None,
    'abstract' : 'Pre-registration and welcome event in Kro Bar on Oxford '
                 'Road. Food and drinks available for purchase.',
    'persons' : ['GUADEC Team'],
    'recording': { 'license' : 'no-video', 'optout' : 'true' },
    'language' : 'eng',
    'type' : '',
    'id' : eventid,
})
eventid += 1

events.append({
    'title' : 'GNOME 20th Birthday Party @ MOSI',
    'subtitle' : None,
    'logo' : None,
    'track' : None,
    'links' : None,
    'attachments' : None,
    'abstract' : 'Celeberate the 20th anniversary of the GNOME project in style at the '
                 'Museum of Science and Industry. Buffet food is provided and drinks '
                 'will be available for purchase.',
    'persons' : ['GUADEC Team'],
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
        print(slot_day)
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

event_ignored_tags = {'id', 'guid', 'matchby', 'day', 'placed', 'abstract_title' }
event_ensure_tags = { 'logo', 'description', 'recording', 'track', 'links', 'attachments' }

conference = {
  'days' : 3,
  'title' : 'GUADEC 2017',
  'start' : '2017-07-28',
  'end' : '2017-07-30',
  'day_change': '00:00',
  'acronym' : 'GUADEC2017',
  'city' : 'Manchester, UK',
  'venue' : 'Manchester Metropolitan University',
  'timeslot_duration' : '00:15', # What does this mean?
}

def add_elements(et, elements, ignore=set()):
    for key, val in sorted(elements.items()):
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

person_id_dict = dict()
def person_id(name):
    if name not in person_id_dict:
        person_id_dict[name] = len(person_id_dict) + 1
    return person_id_dict[name]

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

            if 'guid' not in event:
                event['guid'] = uuid.uuid5(namespace_uuid, str(event['id']))


            event['date'] = start.isoformat()
            event['duration'] = "%02i:%02i" % (dseconds // (60 * 60), dseconds // (60) % 60)

            # Work around https://github.com/Wilm0r/giggity/issues/16
            event = copy.copy(event)
            event['description'] = event['abstract']
            del event['abstract']

            ev = ET.SubElement(room, 'event')
            ev.attrib['id'] = str(event['id'])
            ev.attrib['guid'] = str(event['guid'])
            add_elements(ev, event, event_ignored_tags)

            # Assign IDs to each <person>
            for event_person in ev.find('persons'):
                event_person.set('id', str(person_id(event_person.text)))

    if day_start:
        day.attrib['start'] = day_start.isoformat()
        day.attrib['end'] = day_end.isoformat()

open('schedule.xml', 'bw').write(ET.tostring(schedule, encoding='UTF-8'))


###

table_pagename = '/schedule/'
abstracts_pagename = '/talks-and-events/'

html_table = ET.Element('div')

html_table.attrib['class'] = "schedule"


abstracts = {}

for dayid in range(1, conference['days'] + 1):
    tmp = ET.SubElement(html_table, 'h3')

    date = datetime.datetime.strptime(conference['start'], '%Y-%m-%d')
    date = date.date() + datetime.timedelta(days=dayid - 1)

    tmp.text = date.strftime('%A %d. %B %Y')

    table = ET.SubElement(html_table, 'table')
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

            room_index = rooms.index(event['room'])
            if room_index < len(td_rooms):
                # This is a normal conference room
                td = td_rooms[room_index]
                td.attrib['class'] = 'talk'
            else:
                # This is "elsewhere": replace will a cell that fills the whole row
                colspan = len(td_rooms)
                for td in td_rooms[1:]:
                    tr.remove(td)
                td = td_rooms[0]
                td.attrib['colspan'] = str(colspan)
                td.attrib['class'] = 'break'

            cross_link = event['slug']
            abstract_title = event['title']
            unspecific_location = False
            no_anchor = False
            if 'abstract_title' in event:
                unspecific_location = True
                cross_link = event['abstract_title']
                abstract_title = event['abstract_title']
                # Let the link back go to the first instance that was found
                if abstract_title in abstracts:
                    no_anchor = True

            if 'abstract' in event and event['abstract']:
                div = ET.Element('div')
                div.attrib['class'] = 'abstract'
                div.attrib['id'] = 'abstract-' + cross_link

                header = ET.SubElement(div, 'h4')
                a = ET.SubElement(header, 'a')
                a.text = abstract_title
                a.attrib['href'] = '%s#%s' % (table_pagename, cross_link)

                details = ET.SubElement(div, 'span')
                details.attrib['class'] = 'details'
                if unspecific_location:
                    details.text = 'At different times'
                else:
                    details.text = 'On ' + date.strftime('%A') + ' at ' + event['start'] + ' (' + event['room'] + ')'
                if event['persons']:
                    details.text += ' by ' + ', '.join(event['persons'])

                abstract = event['abstract'].split('<br><br>')
                for paragraph in abstract:
                    p = ET.SubElement(div, 'p')
                    first = True
                    for line in paragraph.split('<br>'):
                        if not first:
                            br = ET.SubElement(p, 'br')
                            br.tail = line
                        else:
                            first = False
                            p.text = line

                if abstract_title not in abstracts:
                    abstracts[abstract_title] = div


            if not no_anchor:
                td.attrib['id'] = cross_link

            header = ET.SubElement(td, 'span')
            header.attrib['style'] = 'font-weight: bold'

            if 'abstract' in event and event['abstract']:
                hdrtext = ET.SubElement(header, 'a')
                hdrtext.attrib['href'] = '%s#abstract-%s' % (abstracts_pagename, cross_link)
            else:
                hdrtext = header

            hdrtext.text = event['title']

            if event['persons']:
                br = ET.SubElement(td, 'br')
                br.tail = ', '.join(event['persons'])


html_abstracts = ET.Element('div')
tmp = ET.SubElement(html_abstracts, 'h3')
tmp.text = 'Abstracts'

for title in sorted(abstracts):
    html_abstracts.append(abstracts[title])





tree = ET.ElementTree(html_table)
tree.write('schedule.html', encoding='UTF-8', xml_declaration=False)

tree = ET.ElementTree(html_abstracts)
tree.write('talks-and-events.html', encoding='UTF-8', xml_declaration=False)


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

