
import json
import urllib2
import urlparse
from bs4 import BeautifulSoup

import config

OUTPUT_DATA = {}


def get_url_data(url):
    request = urllib2.Request(url, headers={'User-Agent': 'Magic Browser'})
    response = urllib2.urlopen(request)
    return response


def get_country_asn_data(url, country):
    global OUTPUT_DATA

    print 'Getting ASN for country {0}'.format(country)

    data = get_url_data(url).read()

    soup = BeautifulSoup(data, 'html.parser')
    table = soup.find(lambda tag: tag.name == 'table' and tag['id'] == 'asns')

    if table is None:
        print 'No active ASNs found for country {0}'.format('country')
        return

    rows = table.findAll(lambda tag: tag.name == 'tr')

    headers = [s.text for s in soup.findAll('th')]

    for row in rows[1:]:
        d = [s.text for s in row.findAll('td')]

        data = dict(zip(headers[1:], d[1:]))
        data['country'] = country
        OUTPUT_DATA[d[0].strip('ASN')] = d

    print OUTPUT_DATA


def dump_to_file():
    with open(config.OUTPUT_FILE, 'wb') as f:
        json.dumps(OUTPUT_DATA, f)


def main():
    url = '{0}{1}'.format(config.HOME_PAGE_URL, config.START_PAGE)
    data = get_url_data(url).read()

    soup = BeautifulSoup(data, 'html.parser')
    for tag in soup.findAll('a', href=True):
        if '/country/' not in tag['href']:
            continue

        link = urlparse.urljoin(config.HOME_PAGE_URL, tag['href'])
        if not link:
            continue

        country = tag['href'].strip('/country/')
        get_country_asn_data(link, country)
        break

    dump_to_file()


if __name__ == '__main__':
    main()
