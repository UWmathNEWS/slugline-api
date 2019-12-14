from bs4 import BeautifulSoup, NavigableString, Tag
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

import re
import copy
import xml.etree.ElementTree as ETree

from content.models import Issue, Article

"""A dictionary of XML namespaces the dump uses.
"""
XML_NS = {
    'content': 'http://purl.org/rss/1.0/modules/content/'
}

# Taken from https://developer.mozilla.org/en-US/docs/Web/HTML/Block-level_elements
BLOCK_TAGS = { 'address', 'article', 'aside', 'blockquote', 'details', 'dialog'
                'dialog', 'dd' 'div', 'dl', 'dt', 'fieldset', 'figcaption', 'figure'
                'footer', 'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header', 'hgroup'
                'hr', 'li', 'main', 'nav', 'ol', 'p', 'pre', 'section', 'table', 'ul'}

class Command(BaseCommand):
    help = 'Import articles from a dump of the WordPress site'

    def add_arguments(self, parser):
        parser.add_argument('dump_file')

    def get_issue_numbers(self, issue_code):
        regex = r'v([0-9]+)i([0-9]+)'
        match = re.match(regex, issue_code)
        if match:
            return int(match.group(1)), int(match.group(2))
        else:
            return None


    def is_block_element(self, elem):
        """Returns true if tag is a block-level element in HTML.
        """
        if isinstance(elem, NavigableString):
            return False
        else:
            return elem.name in BLOCK_TAGS

    def parse_wordpress_html(self, content):
        """Reads in raw HTML from a Wordpress dump and does some
        post-processing to add paragraph breaks and attempt to 
        extract the author name.
        """
        content_soup = BeautifulSoup(content, features='html.parser')
        new_soup = BeautifulSoup(features='html.parser')
        for elem in content_soup.children:
            if isinstance(elem, NavigableString):
                # Split on double new lines to form paragraphs
                paras = str(elem).split('\n\n')
                # If the last element in the new tree is a <p> and its last child is inline
                # then the current paragraph was broken by that inline element and we have
                # to put it back together.
                try:
                    if new_soup.contents[-1].name == 'p' and not self.is_block_element(new_soup.contents[-1].contents[-1]):
                        new_soup.contents[-1].append(paras[0])
                        paras = paras[1:]
                except IndexError:
                    # either new_soup has no children, or the last element in new_soup
                    # has no children, so forget about it
                    pass
                for para in paras:
                    p_tag = new_soup.new_tag('p')
                    p_tag.string = para.strip()
                    new_soup.append(p_tag)
            elif self.is_block_element(elem):
                new_soup.append(copy.copy(elem))
            else:
                if len(new_soup.contents) == 0:
                    p_tag = new_soup.new_tag('p')
                    p_tag.append(copy.copy(elem))
                    new_soup.append(p_tag)
                else:
                    new_soup.contents[-1].append(copy.copy(elem))
        author_tag = new_soup.contents[-1].extract()
        return new_soup.prettify(), author_tag.text 

    def article_from_tag(self, article_tag):
        title = article_tag.find('title').text or ''
        content = article_tag.find('content:encoded', XML_NS).text
        post_tags = article_tag.findall(r'.//category[@domain="post_tag"]')
        # Loop through all the tags until we find one that matches a version number
        volume_num = None
        issue_num = None
        for tag in post_tags:
            issue_code = tag.text
            result = self.get_issue_numbers(issue_code)
            if result != None:
                volume_num, issue_num = result
                break
        if issue_num == None or volume_num == None:
            # this doesn't have a valid issue tag, forget about it
            return None
        issue, _ = Issue.objects.get_or_create(
            issue_num=issue_num,
            volume_num=volume_num
        )
        # get rid of the mysterious &nbsp's Wordpress insists on putting everywhere
        content = content.replace('&nbsp;', ' ').strip()
        content_html, author = self.parse_wordpress_html(content)
        return Article(
            title=title,
            slug=slugify(title),
            author=author,
            content_html=content_html,
            issue=issue,
            is_wordpress=True
        )

    def handle(self, *args, **options):
        self.stdout.write('WARNING: This will delete all existing Wordpress articles!')
        self.stdout.write('Backup the database before continuing.')
        input('Press ENTER to continue...')
        # Delete existing Wordpress articles
        Article.objects.filter(is_wordpress=True).delete()
        file_name = options['dump_file']
        tree = ETree.parse(file_name)
        article_tags = tree.findall('.//item')
        articles = filter(None, map(lambda tag: self.article_from_tag(tag), article_tags))
        Article.objects.bulk_create(articles)

