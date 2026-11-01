Digital Forensics Investigation Report Generator

A Python-based Digital Forensics Investigation Report Generator designed to simplify the creation and management of digital forensic investigation reports. The application provides an interactive interface for managing investigation details and generating structured PDF reports.

🚀 Getting Started

Follow these steps to set up and run the project locally on another machine.

1. Prerequisites

Ensure you have Python 3.9 or higher installed on your system.

Download Python: https://www.python.org/downloads/

2. Clone the Repository

git clone https://github.com/BhumikaShelar/Digital-Forensics-Investigation-Report-Generator.git
cd Digital-Forensics-Investigation-Report-Generator

3. Install Dependencies

Install the required Python packages:

pip install streamlit

If a requirements.txt file is available in the repository, install all dependencies using:

pip install -r requirements.txt

4. Configure Environment Variables

If the project requires environment variables, create a .env file in the root directory and configure the required credentials.

# Example
DATABASE_URL=your_database_connection_string

5. Run the Application

Development Mode (Recommended for testing):

Run the Streamlit application:

streamlit run app.py

Open http://localhost:8501 in your browser to view the application.

📁 Project Structure

app.py - Main application file containing the Streamlit interface

database.py - Handles database operations and investigation data management

pdf_generator.py - Generates PDF investigation reports

sample_data.py - Contains sample investigation data

reports/ - Stores generated investigation reports

exports/ - Stores exported files

.gitignore - Excludes unnecessary files and sensitive information

LICENSE - Project license information

README.md - Project documentation

🛠️ Technologies Used

Python - Core application development

Streamlit - Interactive web application interface

Database - Investigation data management

PDF Generation - Creating structured investigation reports

🔍 Features

Generate structured digital forensic investigation reports

Manage investigation-related information

Store investigation data using database functionality

Generate and export PDF reports

Interactive and user-friendly interface

Sample investigation data for demonstration

🔐 Ethical Use

This project is intended for educational purposes and authorized digital forensic investigations. Users should ensure that all evidence is collected, handled, and documented in accordance with applicable laws and forensic best practices.
