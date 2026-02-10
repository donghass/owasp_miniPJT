import os

from app import create_app, db
from app.models import Complaint, Notice, Post, User

app = create_app()


@app.cli.command("init-db")
def init_db_cli():
    db.create_all()
    ensure_default_admin()
    print("Database initialized.")


def ensure_default_admin():
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(
            username="admin",
            email="admin@example.com",
            full_name="System Admin",
            phone="010-0000-0000",
            role="admin",
        )
        admin.set_password("admin1234")
        db.session.add(admin)
        db.session.commit()
    return admin


def ensure_user(username, email, full_name, phone, password):
    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            phone=phone,
            role="user",
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
    return user


@app.cli.command("seed-demo")
def seed_demo_cli():
    db.create_all()
    admin = ensure_default_admin()
    user1 = ensure_user("user1", "user1@example.com", "Hong Gil Dong", "010-1111-1111", "user12345")
    user2 = ensure_user("user2", "user2@example.com", "Kim Min Ji", "010-2222-2222", "user12345")

    post_titles = {"서비스 개선 요청", "진료 예약 시스템 문의"}
    for title in post_titles:
        post = Post.query.filter_by(title=title, user_id=user1.id).first()
        if not post:
            db.session.add(
                Post(
                    title=title,
                    content="데모 데이터로 생성된 게시물입니다.",
                    user_id=user1.id,
                )
            )
    db.session.commit()

    notice_data = [
        ("시스템 점검 안내", "이번 주말 시스템 점검이 예정되어 있습니다.", True),
        ("내부 공지", "관리자 전용 비공개 공지입니다.", False),
    ]
    for title, content, is_published in notice_data:
        notice = Notice.query.filter_by(title=title).first()
        if not notice:
            db.session.add(
                Notice(
                    title=title,
                    content=content,
                    is_published=is_published,
                    created_by=admin.id,
                )
            )
    db.session.commit()

    complaint_titles = {"진료비 영수증 문의", "개인정보 열람 요청"}
    for title in complaint_titles:
        complaint = Complaint.query.filter_by(title=title, user_id=user1.id).first()
        if not complaint:
            db.session.add(
                Complaint(
                    title=title,
                    content="데모 데이터로 생성된 민원입니다.",
                    category="general",
                    user_id=user1.id,
                )
            )
    db.session.commit()

    print("Demo data seeded: admin, user1, user2, posts, notices, complaints.")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        ensure_default_admin()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=True)
