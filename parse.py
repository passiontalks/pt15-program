#!/usr/bin/env python3

import argparse, csv, os, re, sys

def sanitize(table):
    return [[re.sub(r'\xa0', ' ', y) for y in x] for x in table]

def active(table):
    return [row for row in table if row['Active'] == 'Y']

def rotate(table):
    return [dict(zip(table[0], row)) for row in table[1:]]

prune = set(['', 'a', 'of', 'the', 'and', 'to', 'as', 'be', 'us', 'is', 'in', 'how', 'with', 'how', 'from', 'i', 'can', 'it', 'who', 'our'])
def urlize(title):
    words = [re.sub(r'[^A-Za-z0-9]', '', word)
             for word in title.lower().strip().split()]
    return '-'.join([word for word in words if word not in prune][:5])

def render_singlepage(table, filename):
    with open(filename, 'w') as f:
        for row in sorted(table, key=lambda x: (x['Session'].strip(),
                                                x['Timeslot'].strip())):
            print('# <span class="talk-title">%s</span>' % (
                row['Talk Title'].strip()), file=f)
            print(file=f)
            print('## <span class="talk-speaker">%s</span>' % (
                row['Full Name'].strip()), file=f)
            print(file=f)
            print('Session %s, %s, Room %s' % (
                row['Session'].strip(),
                row['Timeslot'].strip().replace(' ', '').lower(),
                row['Room'].strip()), file=f)
            print(file=f)
            print('### <span class="talk-abstract">Abstract</span>', file=f)
            print(file=f)
            print(row['Talk Abstract'], file=f)
            print(file=f)
            if row['Privacy: Bio'] != 'X':
                print('### <span class="talk-bio">Bio</span>', file=f)
                print(file=f)
                print(row['Professional Bio'], file=f)
                print(file=f)
            print('### <span class="talk-faith">Statement of Faith</span>', file=f)
            print(file=f)
            print(row['Statement of Faith'], file=f)
            print(file=f)

def render_index(table, filename):
    with open(filename, 'w') as f:
        index = {}
        tracks = {}
        times = set()
        for row in table:
            session, track = row['Session'].strip()
            time = row['Timeslot'].strip().replace(' ', '').lower()
            if time not in index:
                index[time] = {}
            index[time][track] = row
            tracks[track] = row['Room'].strip()
            times.add(time)
        print('<table class="table table-striped">', file=f)
        print('  <thead>', file=f)
        print('    <tr>', file=f)
        print('      <th>Time</th>', file=f)
        for track in sorted(tracks.keys()):
            print('      <th>Track %s<br/>Room %s</th>' % (
                track, tracks[track]), file=f)
        print('    </tr>', file=f)
        print('  </thead>', file=f)
        print('  <tbody>', file=f)
        for time in sorted(times):
            print('    <tr>', file=f)
            print('      <th>%s</th>' % time, file=f)
            for track in sorted(tracks.keys()):
                if time in index and track in index[time]:
                    row = index[time][track]
                    title = row['Talk Title'].strip().replace("'", '&rsquo;')
                    basename = urlize(row['Talk Title'])
                    permalink = os.path.join(
                        '{{ site.baseurl }}', 'talk', basename)
                    print("      <td><a href=\"%s\">{{ '%s' | markdownify }}</a></td>" % (
                        permalink, title), file=f)
                else:
                    print('      <td></td>', file=f)
            print('    </tr>', file=f)
        print('  </tbody>', file=f)
        print('</table>', file=f)

def render_pages(table, dirname):
    for row in table:
        basename = urlize(row['Talk Title'])
        filename = os.path.join(dirname, '%s.md' % basename)
        permalink = os.path.join(dirname, basename, 'index.html')
        with open(filename, 'w') as f:
            print('---', file=f)
            print('layout: page', file=f)
            print('title: "%s"' % re.sub(r'"', r'\"', row['Talk Title'].strip()), file=f)
            print('permalink: "%s"' % permalink, file=f)
            print('---', file=f)
            print(file=f)
            print('## <span class="talk-speaker">%s</span>' % (
                row['Full Name'].strip()), file=f)
            print(file=f)
            print('Session %s, %s, Room %s' % (
                row['Session'].strip(),
                row['Timeslot'].strip().replace(' ', '').lower(),
                row['Room'].strip()), file=f)
            print(file=f)
            print('### <span class="talk-abstract">Abstract</span>', file=f)
            print(file=f)
            print(row['Talk Abstract'], file=f)
            print(file=f)
            if row['Privacy: Bio'] != 'X':
                print('### <span class="talk-bio">Bio</span>', file=f)
                print(file=f)
                print(row['Professional Bio'], file=f)

def driver(input, output, mode):
    with open(input, 'r') as f:
        table = list(csv.reader(f))
    table = active(rotate(sanitize(table)))
    if mode == 'singlepage':
        render_singlepage(table, output)
    elif mode == 'index':
        render_index(table, output)
    elif mode == 'pages':
        render_pages(table, output)
    else:
        assert(False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('-o', '--output', required=True)
    parser.add_argument('-m', '--mode',
                        choices=set(['singlepage', 'index', 'pages']),
                        required=True)
    args = parser.parse_args()
    driver(args.input, args.output, args.mode)
