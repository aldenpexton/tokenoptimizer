from setuptools import setup, find_packages

setup(
    name="tokenoptimizer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "Flask==2.3.2",
        "python-dotenv==1.0.0",
        "supabase==1.0.3",
        "gunicorn==21.2.0",
        "Flask-CORS==4.0.0",
        "python-dateutil==2.8.2",
        "requests==2.31.0",
        "openai>=0.28.0"
    ],
) 