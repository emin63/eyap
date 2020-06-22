"""Commands providing eyap interface to GitHub
"""

import getpass
import click

from eyap.utils.ghtools import gparse


@click.group()
def cli():
    "Group of available commands."


@cli.command()
@click.option('--user', help='User to use in connecting to github.')
@click.option('--authfile', help=(
    'Optional authinfo file to get user and password from.'))
@click.option('--query', help=(
    'GitHub search query to get issues (e.g. "is:open is:issue".'))
@click.argument('outcsv')
@click.option('--password', help='Password or token to connect to github.')
def issues2csv(user, query, outcsv, authfile, password):
    """Search github for issues given by query and save to outcsv.

For example, you can run a command like

   ghub.py issues2csv --authfile ~/.authinfo \
     --query 'is:open is:issue repo:emin63/eyap' /tmp/out.csv

to run a query to get all open issues out of the emin63/eyap repo
into the file /tmp/out.csv
    """
    if authfile:
        if user or password:
            raise ValueError('Cannot provide user/password if authfile given')
        user, password = gparse.parse_auth_info(authfile)
        if not user:
            raise ValueError('Could not parse authfile %s' % authfile)
    if not user:
        raise ValueError('Must provide value for --user')
    if not password:
        password = getpass.getpass(f'GitHub password for {user}: ')

    gparse.get_issues_to_csv(user, password, query, outcsv)
    click.echo('Output in %s' % outcsv)


if __name__ == '__main__':
    cli()
