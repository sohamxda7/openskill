# Author: Soham Sen <sensoham135@gmail.com>
# Repository: https://github.com/sohamxda7/openskill

"""Project metadata shared by user-facing OpenSKILL surfaces."""

PROJECT_NAME = "OpenSKILL"
PROJECT_AUTHOR_NAME = "Soham Sen"
PROJECT_AUTHOR_EMAIL = "sensoham135@gmail.com"
PROJECT_AUTHOR = "%s <%s>" % (PROJECT_AUTHOR_NAME, PROJECT_AUTHOR_EMAIL)
PROJECT_REPOSITORY_URL = "https://github.com/sohamxda7/openskill"
PROJECT_RELEASES_URL = PROJECT_REPOSITORY_URL + "/releases"
PROJECT_LICENSE = "GPL-3.0-or-later"


def about_lines(version=None):
    lines = [PROJECT_NAME]
    if version:
        lines.append("Version: %s" % version)
    lines.extend(
        [
            "Author: %s" % PROJECT_AUTHOR,
            "Repository: %s" % PROJECT_REPOSITORY_URL,
            "Releases: %s" % PROJECT_RELEASES_URL,
            "License: %s" % PROJECT_LICENSE,
        ]
    )
    return lines


def about_text(version=None):
    return "\n".join(about_lines(version))
