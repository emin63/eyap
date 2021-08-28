"""GitHub data parser.
"""

import logging
import re
import csv
from eyap import github_comments


def get_issues_to_csv(user, passwd, query, outfile):
    """Get issues from github into a CSV file.

    :param user:    String name of github user.

    :param passwd:  String name of github password or token.

    :param query:   String query to github search.

    :param outfile: Path to output file.

    ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    PURPOSE:  Write desired issues to outfile.

    """
    fieldnames, rows = get_row_data(user, passwd, query)
    with open(outfile, 'w') as my_fd:
        writer = csv.DictWriter(my_fd, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def get_row_data(user, passwd, query, raw=None, page=20,
                 partial_get=None):
    """Git row data from github for desired query.

    :param user:    String name of github user.

    :param passwd:  String name of github password or token.

    :param query:   String query to github search.

    ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    :return:  The pair (fieldnames, rows) where fieldnames is a list
              of string filed names and rows is a list of lists with the
              data for the given fields.

    ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    PURPOSE:  Get data from github.

    """
    fieldnames = ['number', 'title', 'assignees', 'labels', 'url', 'state',
                  'updated_at']
    query = query if query else 'is: issue'
    data, header = github_comments.GitHubCommentThread.raw_search(
        user, passwd, query, page=page)
    logging.debug('Got response header from github: %s', header)
    if data['total_count'] != len(data['items']):
        if partial_get:
            partial_get['status'] = (data['total_count'], len(data['items']))
        else:
            raise ValueError('Could not get all items.')
    rows = [{'number': item['url'].split('/')[-1], 'url': item['html_url'],
             'title': item['title'], 'assignees': '/'.join([
                 i['login'] for i in item['assignees']]),
             'state': item['state'],
             'updated_at': item['updated_at'],
             'labels': '/'.join([i['name'] for i in item['labels']])}
            for item in data['items']]
    if raw is not None:
        raw['data'] = data
    return fieldnames, rows


def parse_auth_info(fname: str) -> (str, str):
    """Parse username/passwd from file.

    :param fname:   String path to file to parse.

    ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    :return:  The pair (username, passwd) parsed from file or (None, None).

    ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    PURPOSE:  Parse auth info from file.

    """
    my_re = re.compile(
        '(?P<user>[-0-9a-zA-Z_]+).magithub ' +
        '*password *(?P<passwd>[0-9a-zA-Z]+)')
    data = open(fname).read()
    for line in data.split('\n'):
        match = my_re.search(line)
        if match:
            return match.group('user'), match.group('passwd')
    return None, None
