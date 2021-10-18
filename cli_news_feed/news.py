import feedparser
import locale
import calendar
import time
from datetime import datetime
import dateutil.parser
from rich.console import Console


url = 'https://www.nrk.no/nyheter/siste.rss'
# url = 'http://feeds.bbci.co.uk/news/world/rss.xml'
console = Console(width=50)
locale.setlocale(locale.LC_ALL, 'nb_NO')


def prettify_date(date_text):
    date = datetime.strptime(date_text, '%Y-%m-%dT%H:%M:%S%z')
    # Index 0 in months list is empty
    norwegian_month = list(calendar.month_name)[date.month]
    west = date.astimezone(dateutil.tz.gettz('W. Europe Standard Time'))
    return datetime.strftime(west, f'%d. {norwegian_month} %Y - %H:%M')


def print_entries(entries, console):
    for entry in reversed(entries):
        console.rule(f'[bold #cff1fc] {entry.title}', align='center')
        pretty_date = prettify_date(entry.updated)
        console.print(pretty_date, justify='left', style='italic #ccfce2')
        console.print(entry.description, overflow='fold', end='\n\n')


def main():
    raw = feedparser.parse(url)
    print_entries(raw.entries, console)
    last_updated = dateutil.parser.isoparse(raw.feed.updated)
    running = True
    while running:
        raw = feedparser.parse(url)
        # The isoparse-method from datetime is not
        # designed to parse arbitrary ISO 8601 strings
        latest_update = dateutil.parser.isoparse(raw.feed.updated)
        if latest_update > last_updated:
            last_updated = latest_update
            print_entries(raw.entries, console)
        time.sleep(5*60)


if __name__ == '__main__':
    main()
