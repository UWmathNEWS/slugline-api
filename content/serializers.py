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
        read_only_fields = ("publish_date", "pdf")
        # override the default unique_together message
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Issue.objects.all(),
                fields=("volume_num", "issue_num"),
                message="ISSUE.ALREADY_EXISTS",
            )
        ]


class ArticleSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=False, default="")
    sub_title = serializers.CharField(required=False, default="")
    article_type = serializers.CharField(required=False, default=Article.Type.SLATE)
    issue = serializers.PrimaryKeyRelatedField(
        required=False,
        default=lambda: Issue.objects.latest_issue(),
        queryset=Issue.objects.all(),
    )

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
        read_only_fields = ("slug", "is_article_of_issue", "is_promo", "user")


class ArticleContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ("content_raw",)


class ArticleHTMLSerializer(serializers.ModelSerializer):
    html = serializers.CharField(source="render_to_html", read_only=True)

    class Meta:
        model = Article
        fields = ("html",)
