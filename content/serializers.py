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
    class Meta:
        model = Article
        fields = (
            "id",
            "title",
            "slug",
            "sub_title",
            "author",
            "article_type",
            "is_article_of_issue",
            "is_promo",
            "issue",
            "user",
        )


class ArticleContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ("content_raw",)


class ArticleHTMLSerializer(serializers.ModelSerializer):

    html = serializers.CharField(source="render_to_html", read_only=True)

    class Meta:
        model = Article
        fields = ("html",)
