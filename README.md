🥗 Kalorio

Kalorio is a simple application designed to help users manage and track their daily calorie intake. The app allows users to log meals, monitor total calories consumed, and compare their intake against a daily goal, supporting healthier eating habits through better awareness.

This project was created as a learning exercise, focusing on building core application features such as user authentication, CRUD operations, and structured data handling.

✨ Features

👤 User Authentication
Users can register and log in to manage their personal calorie data.

🍽️ Meal Tracking
Add meals with calorie values throughout the day.

📊 Daily Calorie Summary
View total calories consumed per day and track progress toward a daily goal.

✏️ Edit & Delete Entries
Modify or remove meal entries to keep data accurate.

📅 Date-based Tracking
Calorie intake is organized by day for easy review.

🌐 User Pages & Data Exploration
User pages show statistics and the data items each user has added.

🗂️ Data Classification
A user can assign one or more classifications to a data item, with the available categories stored in the database.

💬 Collaborative Notes
A user can add additional information about another user's data item, and it is visible within the application (messages).

📰 Community Feed
Browse the latest published meals from all users on the front page.

📣 Publish Meals
Publish a logged meal to make it visible in the community feed.

🗨️ Comments
Leave comments on published meals.

🎯 Daily Goal Management
Set or update a personal daily calorie goal from the user profile.

🗓️ Calendar Navigation
Navigate by date and month to review daily logs.

🎯 Project Goal

The goal of Kalorio is to provide a straightforward and user-friendly way to track calorie intake while serving as a practical project for learning application development concepts.

We aimed to cover all the grade 4 requirements as the final target.

🛠️ Tech Stack

Backend: Flask

Database: SQLite (or other relational database)

Frontend: HTML, CSS, Jinja templates

## Local setup

1. Create and activate a virtual environment (e.g., `python -m venv venv` and `source venv/bin/activate`).
2. Install dependencies: `pip install flask werkzeug`
3. Create the SQLite database and tables: `sqlite3 kalorio.db < schema.sql` (this generates `kalorio.db` in the repo root; rerun the command if you want to reset the schema).

## Launching the app

1. Start the development server: `flask run`

By default, the server listens on `http://127.0.0.1:5000`; visit `/register`, `/login`, or `/dashboard` once authenticated.
