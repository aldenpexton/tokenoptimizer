from setuptools import setup, find_packages

# Read long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tokenoptimizer",
    version="0.1.0",
    author="TokenOptimizer Team",
    author_email="info@tokenoptimizer.com",
    description="Track and optimize LLM API usage and costs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/tokenoptimizer",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests",
        "python-dotenv",
    ],
    extras_require={
        "dev": [
            "pytest",
            "mock",
        ],
        "openai": ["openai>=0.27.0"],
        "anthropic": ["anthropic>=0.7.0"],
        "mistral": ["mistralai>=0.0.1"],
        "all": [
            "openai>=0.27.0",
            "anthropic>=0.7.0",
            "mistralai>=0.0.1",
        ],
    },
) 