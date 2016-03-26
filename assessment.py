import json
import re
import urllib

# this constant value should belongs to config file, but set here for simple case
MAX_RESULT = 20

def google_search (terms, page=0):
    """Perform a google search and get a set number of result
    :param: terms - search terms for Google
    :param: page - pagination of search result
    :return: print statements 
    :note: This script does not handle security check
    """
    if page < 0:  # check if negative index exist
        raise Exception('Invalid pagination found during search operation')

    # initialize Google search url
    query = urllib.urlencode({'q': str(terms), 'start': page})
    url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&%s' % query

    # retrieve result from Google
    respond = urllib.urlopen(url).read()
    respond = json.loads(respond)
    data = respond['responseData']

    if page == 0:  # report total result only for the first time
        print 'Number of total results: %s' % data['cursor']['resultCount']

    urls = []
    index = data['cursor']['currentPageIndex']
    if int(data['cursor']['resultCount'].replace(',', '')) > 0:
        limit = MAX_RESULT - int(data['cursor']['pages'][index]['start'])
        for content in data['results']:
            urls.append(str(content['url']))
            limit -= 1
            if limit == 0:
                break

    # continue getting results if more pages exists
    pages = data['cursor']['pages'][index+1::]
    if pages and int(pages[0]['start']) < MAX_RESULT:
        next_page = google_search(terms, pages[0]['start'])
        urls.extend(next_page)
        return urls

    return urls

def read_content(url):
    """get content from a website
    :param: url - link to the website
    :return: website contents 
    """
    try:
        data = urllib.urlopen(str(url))
        return data.read()
    except IOError:
        print "The url cannot be found: %s" % url
        return None

def get_paragraph(term, content):
    """Get paragraph that contains desired substring
    :param: term - desired substring
    :param: content - target content
    :return: list of content 
    """
    regex = '\<p>(.*?)\</p>'
    results = re.findall(regex, content)

    paragraphs = []
    if results:
        for result in results:
            result = re.sub("<.*?>", '', result)
            if term.lower() in result.lower():
                i = result.lower().index(term.lower())
                start = max(0, i - 20)
                end = i + len(term) + 30
                paragraphs.append(result[start:end] + '...')

    return paragraphs

search_term = "hello world"
search_term = raw_input('Search term: ')

urls = google_search(search_term)
urls = list(set(urls)) # Remove duplicated links from list

# Provide summary of returned links
print "----top %s links retrieved---" % len(urls)
for url in urls:
    print url

# Print sample content from website
for url in urls:
    try:
        print url
        print "-------------------------------"

        web_content = read_content(url)
        if web_content is None:
            print "Unable to get available data from this site"
            continue

        content = get_paragraph(search_term, web_content)
        if content:
            for text in content:
                print text
            print "\n"
        else:
            print "visit link above for more detail"
    except IOError:
        print "url cannot be read: %s" % url
        continue
