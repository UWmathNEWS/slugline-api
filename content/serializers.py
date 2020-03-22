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

    html = serializers.CharField(source="render_to_html")

    class Meta:
        model = Article
        fields = (
            "id",
            "title",
            "slug",
            "sub_title",
            "author",
            "html",
            "content_raw",
            "is_article_of_issue",
            "is_promo",
            "issue",
            "user",
        )
        read_only_fields = ["html"]
