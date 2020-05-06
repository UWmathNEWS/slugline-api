from django.db import models
from django.contrib import admin

from django.utils.html import strip_tags
from django.utils.text import slugify

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
    issue_code = models.CharField(max_length=1)

    pdf = models.FileField(upload_to="issue_pdfs/", null=True)

    def short_name(self):
        return f"v{self.volume_num}i{self.issue_code}"

    def long_name(self):
        return f"Volume {self.volume_num} Issue {self.issue_code} "

    def __str__(self):
        return self.short_name()

    class Meta:
        unique_together = ("volume_num", "issue_code")
        ordering = ["-volume_num", "-issue_code"]


class Article(models.Model):
    """A generic article class, designed to handle articles from multiple sources.
    """

    class Type(models.TextChoices):
        WORDPRESS = "wordpress"
        SLATE = "slate"

    title = models.CharField(max_length=255)
    slug = models.SlugField()
    """A secondary title that is usually typeset in smaller font below the title."""
    sub_title = models.CharField(max_length=255, blank=True)
    author = models.CharField(max_length=255, blank=True)

    content_raw = models.TextField(default="", blank=True)

    article_type = models.CharField(
        max_length=16, choices=Type.choices, default=Type.SLATE
    )

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)

    is_article_of_issue = models.BooleanField(default=False)
    """Do we want this article to be featured on the issue page?"""
    is_promo = models.BooleanField(default=False)

    user = models.ForeignKey(SluglineUser, on_delete=models.SET_NULL, null=True)

    def render_to_html(self):
        if self.article_type == Article.Type.WORDPRESS:
            return self.content_raw
        elif self.article_type == Article.Type.SLATE:
            raise NotImplementedError(
                "render_to_html not implemented for Slate articles"
            )

    def render_to_xml(self):
        """Returns this article converted to InDesign-compatible XML
        for print export. 
        """
        raise NotImplementedError("render_to_xml not implemented")

    def __str__(self):
        return f"{self.title} by {self.author}"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)


admin.site.register(Issue)
admin.site.register(Article)
