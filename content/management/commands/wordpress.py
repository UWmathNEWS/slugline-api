from django.core.management.base import BaseCommand, CommandError

import re
import xml.etree.ElementTree as ETree

from content.models import Issue, WordpressArticle

"""A dictionary of XML namespaces the dump uses.
"""
XML_NS = {
    'content': 'http://purl.org/rss/1.0/modules/content/'
}

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

    def handle(self, *args, **options):
        # Delete existing Wordpress articles
        WordpressArticle.objects.all().delete()
        file_name = options['dump_file']
        tree = ETree.parse(file_name)
        article_tags = tree.findall('.//item')
        for article_tag in article_tags:
            title = article_tag.find('title').text or ''
            content = article_tag.find('content:encoded', XML_NS).text
            post_tags = article_tag.findall(r'.//category[@domain="post_tag"]')
            # Loop through all the tags until we find one that matches a version number
            for tag in post_tags:
                issue_code = tag.text
                result = self.get_issue_numbers(issue_code)
                if result != None:
                    volume_num, issue_num = result
                    break
            issue, _ = Issue.objects.get_or_create(
                issue_num=issue_num,
                volume_num=volume_num
            )
            article = WordpressArticle(
                title=title,
                issue=issue,
                is_article_of_issue=False,
                is_promo=False
            )
            article.parse_wordpress_html(content)
            article.save()
            

