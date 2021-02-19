from django.contrib.auth.models import Group, Permission

BASE_PERMS = [
    "Can add article",
    "Can change article",
    "Can delete article",
    "Can view article",
    "Can view issue",
]

COPYEDITOR_PERMS = []

EDITOR_PERMS = [
    "Can add user",
    "Can change user",
    "Can delete user",
    "Can view user",
    "Can add issue",
    "Can change issue",
    "Can delete issue",
]

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

    for perm in BASE_PERMS:
        contrib.permissions.add(Permission.objects.get(name=perm))

    for perm in COPYEDITOR_PERMS:
        copyeditor.permissions.add(Permission.objects.get(name=perm))

    for perm in EDITOR_PERMS:
        editor.permissions.add(Permission.objects.get(name=perm))


def role_at_least(role, minimum):
    minimum == role or role in GROUPS.get(minimum, [])
