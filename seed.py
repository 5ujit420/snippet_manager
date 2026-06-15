from faker import Faker
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

import models
from database import Base, SessionLocal, engine

fake = Faker()
pwd_context = PasswordHash((Argon2Hasher(),))

LANGUAGES = ["python", "c", "c++", "rust", "java", "go", "bash", "javascript"]
TAGS = ["cli", "web", "api", "database", "tools", "automation", "linux"]


def seed():
    Base.metadata.create_all(engine)
    db = SessionLocal()

    num_users = int(input("How many users?"))
    num_snippets = int(input("How many snippets?"))

    for _ in range(num_users):
        user = models.User(
            username=fake.user_name(),
            password_hash=pwd_context.hash("fakepass"),
        )
        db.add(user)
    db.commit()

    users = db.query(models.User).all()

    for _ in range(num_snippets):
        import random

        tag_names = random.sample(TAGS, k=2)
        tags = []
        for name in tag_names:
            tag = db.query(models.Tag).filter(models.Tag.name == name).first()
            if not tag:
                tag = models.Tag(name=name)
                db.add(tag)
            tags.append(tag)

        snippet = models.Snippet(
            title=fake.sentence(nb_words=4),
            code=fake.text(max_nb_chars=200),
            language=random.choice(LANGUAGES),
            owner_id=random.choice(users).id,
            tags=tags,
        )
        db.add(snippet)
    db.commit()
    db.close()
    print(f"Seeded {num_users} users and {num_snippets} snippets.")


if __name__ == "__main__":
    seed()
