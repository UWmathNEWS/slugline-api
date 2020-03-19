from django.db import models
from django.contrib import admin

from django.utils.html import strip_tags

from user.models import SluglineUser


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

    pdf = models.FileField(upload_to="issue_pdfs/", null=True)

    def short_name(self):
        return f"v{self.volume_num}i{self.issue_num}"

    def long_name(self):
        return f"Volume {self.volume_num} Issue {self.issue_num} "

    def __str__(self):
        return self.short_name()

    class Meta:

        ordering = ["-volume_num", "-issue_num"]


class ArticleManager(models.Manager):
    def wordpress_articles(self):
        return self.exclude(content_wordpress=None)

    def slate_articles(self):
        return self.exclude(content_slate=None)


class Article(models.Model):
    """A generic article class, designed to handle articles from multiple sources.
    """

    objects = ArticleManager()

    title = models.CharField(max_length=255)
    slug = models.SlugField()
    """A secondary title that is usually typeset in smaller font below the title."""
    sub_title = models.CharField(max_length=255, blank=True)
    author = models.CharField(max_length=255, blank=True)

    """Since we can get articles from data sources, we have both here.
    One and only one of these can be non-null.
    """
    content_wordpress = models.TextField(null=True)
    content_slate = models.TextField(null=True)

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)

    is_article_of_issue = models.BooleanField(default=False)
    """Do we want this article to be featured on the issue page?"""
    is_promo = models.BooleanField(default=False)

    user = models.ForeignKey(SluglineUser, on_delete=models.SET_NULL, null=True)

    def is_wordpress(self):
        return self.content_wordpress != None

    def render_to_html(self):
        """Returns this article converted to HTML for web display."""
        if self.content_wordpress != None:
            return self.content_wordpress
        else:
            raise NotImplementedError(
                "render_to_html not implemented for Slate articles."
            )

    def render_to_xml(self):
        """Returns this article converted to InDesign-compatible XML
        for print export. 
        """
        raise NotImplementedError("render_to_xml not implemented")

    def __str__(self):
        return f"{self.title} by {self.author}"


admin.site.register(Issue)
admin.site.register(Article)

