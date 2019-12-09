from django.db import models
from django.contrib import admin

from django.utils.html import strip_tags

class IssueManager(models.Manager):

    def latest_issue(self):
        return self.all().first()

class Issue(models.Model):
    """An issue of the publication.
    """

    objects = IssueManager()

    publish_date = models.DateField(null=True)

    volume_num = models.IntegerField()
    issue_num = models.IntegerField()

    def short_name(self):
        return f'v{self.volume_num}i{self.issue_num}'

    def long_name(self):
        return f'Volume {self.volume_num} Issue {self.issue_num} '

    def __str__(self):
        return self.short_name()

    class Meta:

        ordering = ['-volume_num', '-issue_num']

class Article(models.Model):
    """A generic article class, designed to handle articles from multiple sources.
    """

    title = models.CharField(max_length=255)
    """A secondary title that is usually typeset in smaller font below the title."""
    sub_title = models.CharField(max_length=255, blank=True)
    author = models.CharField(max_length=255, blank=True)

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)

    def render_to_html(self):
        """Returns this article converted to HTML for web display.
        """
        raise NotImplementedError('render_to_html not implemented')

    def render_to_xml(self):
        """Returns this article converted to InDesign-compatible XML
        for print export. 
        """
        raise NotImplementedError('render_to_xml not implemented')

    def __str__(self):
        return f'{self.title} by {self.author}'

    class Meta:
        abstract = True


class WordpressArticle(Article):
    """An article imported from the Wordpress dump. Some fields may be missing.
    """

    """This is raw HTML extracted from the Wordpress dump."""
    content_html = models.TextField()

    def parse_wordpress_html(self, content):
        """Reads in raw HTML from a Wordpress dump and does some
        post-processing to add paragraph breaks and attempt to 
        extract the author name
        """
        paragraphs = content.split('\n')
        # This is ghetto, but should be fine
        self.author = strip_tags(paragraphs[-1])
        for idx, paragraph in enumerate(paragraphs):
            paragraph + '<p>' + paragraph + '</p>'
            paragraphs[idx] = paragraph
        self.content_html = '\n'.join(paragraphs)
    
admin.site.register(Issue)
admin.site.register(WordpressArticle)
