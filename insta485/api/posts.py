"""REST API for posts."""
import flask

import insta485
from insta485.api.helper import check_authorization, get_post_by_id


@insta485.app.route('/api/v1/')
def get_services():
    """Return a list of services available."""
    context = {
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
        "posts": "/api/v1/posts/",
        "url": "/api/v1/"
    }
    return flask.jsonify(**context)


@insta485.app.route('/api/v1/posts/')
def get_posts():
    """Return the 10 newest posts."""
    connection = insta485.model.get_db()

    logname = check_authorization()

    # get newest post id
    cur = connection.execute(
        "SELECT * FROM posts ORDER BY postid DESC"
    )
    newest_id = cur.fetchone()['postid']

    # get arguments
    size = flask.request.args.get("size", default=10, type=int)
    postid_lte = flask.request.args.get("postid_lte",
                                        default=newest_id, type=int)
    page = flask.request.args.get("page", default=0, type=int)
    if page < 0 or size < 0:
        return flask.jsonify({}), 400

    # Query database
    # fetch all posts
    cur = connection.execute(
        "SELECT * "
        "FROM posts post WHERE "
        "post.postid <= ? AND "
        "(EXISTS (SELECT 1 FROM following follow "
        "WHERE follow.username1 = ? "
        "AND follow.username2 = post.owner) "
        "OR post.owner = ?) ORDER BY postid DESC "
        "LIMIT ? OFFSET ?",
        (postid_lte, logname, logname, size, page * size)
    )
    posts = cur.fetchall()

    context = {}
    context["next"] = ""
    if len(posts) >= size:
        context["next"] = "/api/v1/posts/?size=" + str(size) + "&page="\
                + str(page + 1) + "&postid_lte=" + str(postid_lte)
    context["results"] = []
    for post in posts:
        post_in_context = {}
        post_in_context['postid'] = post['postid']
        post_in_context['url'] = "/api/v1/posts/" + str(post['postid']) + "/"
        context["results"].append(post_in_context)
    context["url"] = flask.request.full_path
    if context["url"].endswith('?'):
        context["url"] = context["url"][:-1]
    return flask.jsonify(**context)


@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/')
def get_post(postid_url_slug):
    """Return post on postid."""
    logname = check_authorization()

    connection = insta485.model.get_db()
    # postid out of range
    maxid = connection.execute(
        "SELECT MAX(postid) FROM posts",
    ).fetchone()['MAX(postid)']
    if postid_url_slug > maxid:
        return flask.jsonify({}), 404
    current_post, comments, likes = get_post_by_id(postid_url_slug, connection)

    # check whether to show like or unlike button
    likeid = None
    for like in likes:
        if like['owner'] == logname:
            likeid = like['likeid']
    likes = len(likes)

    # fetch the profile image
    cur = connection.execute(
        "SELECT * "
        "FROM users WHERE username = ?",
        (current_post['owner'],)
    )
    owner_image = cur.fetchone()['filename']

    context = {
        "comments": [],
        "comments_url": "/api/v1/comments/?postid="
                        + str(postid_url_slug),
        "created": current_post['created'],
        "imgUrl": "/uploads/" + current_post['filename'],
        "likes": {},
        "owner": current_post['owner'],
        "ownerImgUrl": "/uploads/" + owner_image,
        "ownerShowUrl": "/users/" + current_post['owner'] + "/",
        "postShowUrl": "/posts/" + str(postid_url_slug) + "/",
        "postid": postid_url_slug,
        "url": "/api/v1/posts/" + str(postid_url_slug) + "/"
    }
    for comment in comments:
        comment_in_context = {}
        comment_in_context['commentid'] = comment['commentid']
        comment_in_context['lognameOwnsThis'] = False
        if comment['owner'] == logname:
            comment_in_context['lognameOwnsThis'] = True
        comment_in_context['owner'] = comment['owner']
        comment_in_context['ownerShowUrl'] = "/users/" + comment['owner'] + "/"
        comment_in_context['text'] = comment['text']
        comment_in_context['url'] = "/api/v1/comments/" \
            + str(comment['commentid']) + "/"
        context['comments'].append(comment_in_context)
    context['likes']['lognameLikesThis'] = likeid is not None
    context['likes']['numLikes'] = likes
    if likeid is None:
        context['likes']['url'] = None
    else:
        context['likes']['url'] = "/api/v1/likes/" + str(likeid) + "/"

    return flask.jsonify(**context)
