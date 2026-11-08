from booklens import create_app


def test_create_app():
    app = create_app("testing")

    assert app is not None
    assert app.config["TESTING"] is True


def test_homepage_route_is_registered():
    app = create_app("testing")

    assert "/" in [rule.rule for rule in app.url_map.iter_rules()]
