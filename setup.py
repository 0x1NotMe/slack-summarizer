from setuptools import setup, find_packages

setup(
    name="slack-summarizer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "slack_sdk>=3.0.0",
        "slack_bolt>=1.18.0",
        "openai>=1.0.0",
        "PyYAML>=6.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "flake8>=6.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "slack-summarizer=slack_summarizer.main:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool to summarize Slack channel conversations using OpenAI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)
