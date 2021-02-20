from django.contrib.auth.models import Group

EDITOR_GROUP = "Editor"
COPYEDITOR_GROUP = "Copyeditor"
CONTRIBUTOR_GROUP = "Contributor"

GROUPS = {
    CONTRIBUTOR_GROUP: [],
    COPYEDITOR_GROUP: [CONTRIBUTOR_GROUP],
    EDITOR_GROUP: [COPYEDITOR_GROUP, CONTRIBUTOR_GROUP],
}


def create_default_groups():
    editor, _ = Group.objects.get_or_create(name=EDITOR_GROUP)
    copyeditor, _ = Group.objects.get_or_create(name=COPYEDITOR_GROUP)
    contrib, _ = Group.objects.get_or_create(name=CONTRIBUTOR_GROUP)

    contrib.permissions.clear()
    copyeditor.permissions.clear()
    editor.permissions.clear()


def role_at_least(role, minimum):
    minimum == role or role in GROUPS.get(minimum, [])
