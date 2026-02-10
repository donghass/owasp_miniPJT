from app import create_app, db
from app.models import Complaint, Notice, User


def _create_user(username, role="user"):
    user = User(
        username=username,
        email=f"{username}@example.com",
        full_name=f"{username} name",
        phone="010-9999-9999",
        role=role,
    )
    user.set_password("pass12345")
    db.session.add(user)
    db.session.commit()
    return user


def _login(client, username, password="pass12345"):
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=False,
    )


def test_register_login_logout_flow(tmp_path):
    db_path = tmp_path / "flow.db"
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
            "SECRET_KEY": "test-secret",
        }
    )

    with app.app_context():
        db.create_all()

    client = app.test_client()

    res = client.post(
        "/register",
        data={
            "username": "usernew",
            "email": "usernew@example.com",
            "full_name": "User New",
            "phone": "010-1111-2222",
            "password": "pass12345",
        },
        follow_redirects=False,
    )
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]

    res = _login(client, "usernew")
    assert res.status_code == 302
    assert res.headers["Location"].endswith("/")

    res = client.get("/logout", follow_redirects=False)
    assert res.status_code == 302
    assert res.headers["Location"].endswith("/")



def test_admin_page_blocked_for_normal_user(tmp_path):
    db_path = tmp_path / "authz.db"
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
            "SECRET_KEY": "test-secret",
        }
    )

    with app.app_context():
        db.create_all()
        _create_user("normal", role="user")

    client = app.test_client()
    _login(client, "normal")

    res = client.get("/admin", follow_redirects=False)
    assert res.status_code == 302



def test_private_notice_is_hidden_for_normal_user(tmp_path):
    db_path = tmp_path / "notice.db"
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
            "SECRET_KEY": "test-secret",
        }
    )

    with app.app_context():
        db.create_all()
        admin = _create_user("adminx", role="admin")
        user = _create_user("member", role="user")
        private_notice = Notice(
            title="private",
            content="hidden",
            is_published=False,
            created_by=admin.id,
        )
        db.session.add(private_notice)
        db.session.commit()

        private_id = private_notice.id
        del user

    client = app.test_client()
    _login(client, "member")

    res = client.get(f"/notices/{private_id}", follow_redirects=False)
    assert res.status_code == 302
    assert "/notices" in res.headers["Location"]



def test_complaint_status_update_admin_only(tmp_path):
    db_path = tmp_path / "complaint.db"
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
            "SECRET_KEY": "test-secret",
        }
    )

    with app.app_context():
        db.create_all()
        admin = _create_user("opsadmin", role="admin")
        user = _create_user("requester", role="user")
        complaint = Complaint(
            title="help",
            content="need support",
            category="general",
            user_id=user.id,
        )
        db.session.add(complaint)
        db.session.commit()
        complaint_id = complaint.id
        admin_name = admin.username

    user_client = app.test_client()
    _login(user_client, "requester")
    res = user_client.post(
        f"/complaints/{complaint_id}", data={"status": "resolved"}, follow_redirects=False
    )
    assert res.status_code == 302

    admin_client = app.test_client()
    _login(admin_client, admin_name)
    res = admin_client.post(
        f"/complaints/{complaint_id}", data={"status": "resolved"}, follow_redirects=False
    )
    assert res.status_code == 302

    with app.app_context():
        updated = db.session.get(Complaint, complaint_id)
        assert updated.status == "resolved"


def test_security_scenarios_admin_only(tmp_path):
    db_path = tmp_path / "security.db"
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
            "SECRET_KEY": "test-secret",
        }
    )

    with app.app_context():
        db.create_all()
        _create_user("secmember", role="user")
        _create_user("secadmin", role="admin")

    user_client = app.test_client()
    _login(user_client, "secmember")
    blocked = user_client.get("/security/scenarios", follow_redirects=False)
    assert blocked.status_code == 302

    admin_client = app.test_client()
    _login(admin_client, "secadmin")
    allowed = admin_client.get("/security/scenarios", follow_redirects=False)
    assert allowed.status_code == 200
    assert b"A01" in allowed.data


def test_admin_users_search_filter_and_pagination(tmp_path):
    db_path = tmp_path / "admin_users.db"
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
            "SECRET_KEY": "test-secret",
        }
    )

    with app.app_context():
        db.create_all()
        _create_user("filteradmin", role="admin")
        for idx in range(12):
            _create_user(f"user{idx:02d}", role="user")

    client = app.test_client()
    _login(client, "filteradmin")

    filtered = client.get("/admin/users?q=user0&role=user&page=1", follow_redirects=False)
    assert filtered.status_code == 200
    assert b"user00" in filtered.data

    page2 = client.get("/admin/users?page=2", follow_redirects=False)
    assert page2.status_code == 200
    assert "페이지 2".encode() in page2.data
