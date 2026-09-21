"""Views, one for each Insta4288 page."""
from insta4288.views.index import show_index
from insta4288.views.uploads import download_file
from insta4288.views.user import show_user
from insta4288.views.followers import show_followers
from insta4288.views.following import show_following
from insta4288.views.post import show_post
from insta4288.views.explore import show_explore
from insta4288.views.accounts import (
    show_login,
    show_create,
    show_edit,
    show_password,
    show_delete,
)

from insta4288.views.likes import update_likes
from insta4288.views.comments import update_comments
from insta4288.views.posts import update_posts
from insta4288.views.follow import update_following
from insta4288.views.logout import logout
