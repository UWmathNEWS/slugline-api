from rest_framework import serializers

from content.models import Article, Issue


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = (
            "id",
            "publish_date",
            "volume_num",
            "issue_num",
            "pdf",
        )


class ArticleSerializer(serializers.ModelSerializer):

    html = serializers.CharField(read_only=True, source="render_to_html")

    class Meta:
        model = Article
        fields = (
            "id",
            "title",
            "slug",
            "sub_title",
            "author",
            "content_raw",
            "article_type",
            "html",
            "is_article_of_issue",
            "is_promo",
            "issue",
            "user",
        )
