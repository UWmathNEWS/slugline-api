from django.db import models

class Issue(models.Model):
    """An issue of the publication.
    """

    publish_date = models.DateField(null=True)

    issue_num = models.IntegerField()
    volume_num = models.IntegerField()

    def short_name(self):
        return f'v{self.volume_num}i{self.issue_num}'

    def long_name(self):
        return f'Volume {self.volume_num} Issue {self.issue_num} '

    def __str__(self):
        return self.short_name()

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

    class Meta:
        abstract = True

class WordpressArticle(Article):
    """An article imported from the Wordpress dump. Some fields may be missing.
    """

    """This is raw HTML extracted from the Wordpress dump."""
    content_html = models.TextField()

    
