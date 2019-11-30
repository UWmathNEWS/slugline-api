from django.db import models

class Issue(models.Model):
    """An issue of the publication.
    """

    publish_date = models.DateField(null=True)

    issue_num = models.IntegerField()
    volume_num = models.IntegerField()

    def short_name(self):
        return f'v{self.issue_num}i{self.volume_num}'

    def long_name(self):
        return f'Issue {self.issue_num} Volume {self.volume_num}'

    def __str__(self):
        return 'Issue ' + 'v' + str(self.issue_num) + 'i' + str(self.volume_num)

class Article(models.Model):
    """A generic article class, designed to handle articles from multiple sources.
    """

    title = models.CharField(max_length=255)
    """A secondary title that is usually typeset in smaller font below the title."""
    sub_title = models.CharField(max_length=255, blank=True)
    author = models.CharField(max_length=255, blank=True)

    issue = models.ForeignKey(Issue)

    def render_to_html(self):
        """Returns this article converted to HTML for web display.
        """
        raise NotImplementedError('render_to_html not implemented')

    def render_to_xml(self):
        """Returns this article converted to InDesign-compatible XML
        for print export. 
        """
        raise NotImplementedError('render_to_xml not implemented')

    class Meta:
        abstract = True

class WordpressArticle(Article):
    """An article imported from the Wordpress dump. Some fields may be missing.
    """

    """This is raw HTML extracted from the Wordpress dump."""
    content_html = models.TextField()

    
