import asyncio
from datetime import date

from app.db.db_connection import session_manager
from app.db.models import Contact, User
from app.services.auth import hash_helper

contacts_data = [
    {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "0991234567",
        "birthday": date(1990, 6, 8),
        "additional_data": "Friend from work",
    },
    {
        "first_name": "Anna",
        "last_name": "Smith",
        "email": "anna.smith@example.com",
        "phone": "0671234568",
        "birthday": date(1995, 6, 10),
        "additional_data": None,
    },
    {
        "first_name": "Mike",
        "last_name": "Johnson",
        "email": "mike.j@example.com",
        "phone": "0501234569",
        "birthday": date(1988, 6, 12),
        "additional_data": "College friend",
    },
    {
        "first_name": "Kate",
        "last_name": "Brown",
        "email": "kate.brown@example.com",
        "phone": "0631234570",
        "birthday": date(2000, 12, 28),
        "additional_data": None,
    },
    {
        "first_name": "Alex",
        "last_name": "Wilson",
        "email": "alex.w@example.com",
        "phone": "0731234571",
        "birthday": date(1992, 3, 15),
        "additional_data": "Gym buddy",
    },
    {
        "first_name": "Sofia",
        "last_name": "Davis",
        "email": "sofia.davis@example.com",
        "phone": "0991234572",
        "birthday": date(1998, 6, 7),
        "additional_data": "Neighbor",
    },
    {
        "first_name": "Liam",
        "last_name": "Miller",
        "email": "liam.miller@example.com",
        "phone": "0671234573",
        "birthday": date(1985, 9, 22),
        "additional_data": None,
    },
    {
        "first_name": "Emma",
        "last_name": "Taylor",
        "email": "emma.taylor@example.com",
        "phone": "0501234574",
        "birthday": date(1993, 6, 11),
        "additional_data": "Book club",
    },
    {
        "first_name": "Noah",
        "last_name": "Anderson",
        "email": "noah.anderson@example.com",
        "phone": "0631234575",
        "birthday": date(1987, 1, 5),
        "additional_data": None,
    },
    {
        "first_name": "Olivia",
        "last_name": "Thomas",
        "email": "olivia.thomas@example.com",
        "phone": "0731234576",
        "birthday": date(1996, 11, 30),
        "additional_data": "Yoga class",
    },
    {
        "first_name": "James",
        "last_name": "Jackson",
        "email": "james.jackson@example.com",
        "phone": "0991234577",
        "birthday": date(1991, 6, 9),
        "additional_data": None,
    },
    {
        "first_name": "Isabella",
        "last_name": "White",
        "email": "isabella.white@example.com",
        "phone": "0671234578",
        "birthday": date(1994, 4, 18),
        "additional_data": "Coworker",
    },
    {
        "first_name": "Lucas",
        "last_name": "Harris",
        "email": "lucas.harris@example.com",
        "phone": "0501234579",
        "birthday": date(1989, 7, 25),
        "additional_data": None,
    },
    {
        "first_name": "Mia",
        "last_name": "Martin",
        "email": "mia.martin@example.com",
        "phone": "0631234580",
        "birthday": date(1997, 2, 14),
        "additional_data": "Valentine's baby",
    },
    {
        "first_name": "Ethan",
        "last_name": "Garcia",
        "email": "ethan.garcia@example.com",
        "phone": "0731234581",
        "birthday": date(1986, 6, 13),
        "additional_data": None,
    },
]


async def seed():
    async with session_manager.session() as session:
        # Create a test user
        test_email = "test@example.com"
        test_password = "password123"
        
        # Hash the password using our service
        hashed_password = hash_helper.get_password_hash(test_password)
        
        # Create user and force is_verified to True so we can log in
        test_user = User(
            email=test_email, 
            password=hashed_password, 
            is_verified=True,
            role="admin"
        )
        session.add(test_user)
        
        # Commit to generate the user.id in the database
        await session.commit()
        await session.refresh(test_user)
        print(f"Created test user: {test_email} / {test_password}")

        # Add contacts and link them to the test user
        for data in contacts_data:
            # Inject user_id into the contact data
            contact = Contact(**data, user_id=test_user.id)
            session.add(contact)
            
        await session.commit()
        print(f"Seeded {len(contacts_data)} contacts for user {test_email}.")


if __name__ == "__main__":
    asyncio.run(seed())