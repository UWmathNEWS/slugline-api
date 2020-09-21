from django.db import models
from django.contrib import admin

from django.core.files import storage

from django.utils.text import slugify

from user.models import SluglineUser

import io
import fitz
from PIL import Image


ISSUE_UPLOAD_DIR = "issue_pdfs"
SIZES = [1, 2]


class OverwriteStorage(storage.FileSystemStorage):
    """https://djangosnippets.org/snippets/976/"""

    def get_available_name(self, name, max_length=None):
        self.delete(name)
        return name


class IssueManager(models.Manager):
    def latest_issue(self):
        return self.all().first()


def get_issue_cover_paths(issue_path, sizes=None):
    """Given a path to an issue, returns the cover image paths. Returns RGB for full colour, and LA for grayscale.

    LA stands for luminosity and alpha; we do not produce an alpha channel, however, and the LA distinction is
    strictly historical.
    """
    if sizes is None:
        sizes = SIZES
    return [
        path
        for size in sizes
        for path in (
            issue_path + ".COVER-RGB-{}x.png".format(size),
            issue_path + ".COVER-LA-{}x.png".format(size),
        )
    ]


class Issue(models.Model):
    """An issue of the publication."""

    class Colour(models.TextChoices):
        BLASTOFF_BLUE = "blastoff-blue"
        CELESTIAL_BLUE = "celestial-blue"
        COSMIC_ORANGE = "cosmic-orange"
        FIREBALL_FUCHSIA = "fireball-fuchsia"
        GALAXY_GOLD = "galaxy-gold"
        GAMMA_GREEN = "gamma-green"
        GRAVITY_GRAPE = "gravity-grape"
        LIFTOFF_LEMON = "liftoff-lemon"
        LUNAR_BLUE = "lunar-blue"
        MARTIAN_GREEN = "martian-green"
        ORBIT_ORANGE = "orbit-orange"
        OUTRAGEOUS_ORCHID = "outrageous-orchid"
        PLANETARY_PURPLE = "planetary-purple"
        PULSAR_PINK = "pulsar-pink"
        REENTRY_RED = "reentry-red"
        ROCKET_RED = "rocket-red"
        SUNBURST_YELLOW = "sunburst-yellow"
        TERRA_GREEN = "terra-green"
        TERRESTIAL_TEAL = "terrestrial-teal"
        VENUS_VIOLET = "venus-violet"
        PASTEL_BLUE = "pastel-blue"
        PASTEL_BUFF = "pastel-buff"
        PASTEL_CANARY = "pastel-canary"
        PASTEL_GOLDENROD = "pastel-goldenrod"
        PASTEL_GREY = "pastel-grey"
        PASTEL_GREEN = "pastel-green"
        PASTEL_ORCHID = "pastel-orchid"
        PASTEL_PINK = "pastel-pink"
        PASTEL_SALMON = "pastel-salmon"
        PAPER = "paper"

    objects = IssueManager()

    publish_date = models.DateField(null=True)

    volume_num = models.IntegerField()
    issue_code = models.CharField(max_length=1)

    pdf = models.FileField(
        upload_to=ISSUE_UPLOAD_DIR, null=True, blank=True, storage=OverwriteStorage()
    )

    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    colour = models.CharField(
        max_length=24, choices=Colour.choices, default=Colour.PAPER
    )

    @property
    def published(self):
        return self.publish_date is not None

    def short_name(self):
        return f"v{self.volume_num}i{self.issue_code}"

    def long_name(self):
        return f"Volume {self.volume_num} Issue {self.issue_code} "

    def __str__(self):
        return self.short_name()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.pdf:
            doc = fitz.Document(self.pdf.path)
            cover = doc[0]
            for size in SIZES:
                cover_pix = cover.getPixmap(matrix=fitz.Matrix(size / 2, size / 2))
                bytes_stream = io.BytesIO(
                    cover_pix.getImageData(output="ppm")
                )  # We use ppm for speed
                cover_la_img = Image.open(bytes_stream).convert("L")

                path_rgb, path_la = get_issue_cover_paths(self.pdf.path, sizes=[size])
                cover_pix.writePNG(path_rgb)
                cover_la_img.save(path_la, "PNG")

    class Meta:
        unique_together = ("volume_num", "issue_code")
        ordering = ["-volume_num", "-issue_code"]


class Article(models.Model):
    """A generic article class, designed to handle articles from multiple sources."""

    class Type(models.TextChoices):
        WORDPRESS = "wordpress"
        SLATE = "slate"

    class Status(models.TextChoices):
        DRAFT = "draft"
        PENDING = "pending"
        IN_PROGRESS = "in-progress"
        OKAYED = "okayed"
        REJECTED = "rejected"

    title = models.CharField(max_length=255)
    slug = models.SlugField()
    """A secondary title that is usually typeset in smaller font below the title."""
    sub_title = models.CharField(max_length=255, blank=True)
    author = models.CharField(max_length=255, blank=True)

    content_raw = models.TextField(default="", blank=True)

    article_type = models.CharField(
        max_length=16, choices=Type.choices, default=Type.SLATE
    )
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.DRAFT
    )

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)

    is_article_of_issue = models.BooleanField(default=False)
    """Do we want this article to be featured on the issue page?"""
    is_promo = models.BooleanField(default=False)

    user = models.ForeignKey(SluglineUser, on_delete=models.SET_NULL, null=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    @property
    def published(self):
        return self.issue.published

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
