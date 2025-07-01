from setuptools import setup, find_packages

setup(
    name="ai-book-agent",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "Flask==3.0.0",
        "Flask-CORS==4.0.0",
        "Werkzeug==3.0.1",
        "firebase-admin==6.4.0",
        "google-cloud-firestore==2.13.1",
        "openai==1.6.1",
        "python-dotenv==1.0.0",
        "requests==2.31.0"
    ],
    python_requires=">=3.8",
    author="AI Book Marketing Agent",
    description="Backend services for autonomous book marketing and social media content generation",
    entry_points={
        "console_scripts": [
            "ai-book-agent=app.main:run_app"
        ]
    }
) 