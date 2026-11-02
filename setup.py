"""Setup configuration for sample-app-python."""

from setuptools import setup, find_packages

setup(
    name="sample-app-python",
    version="0.1.0",
    description="Sample Python FastAPI app using GitHub shared CI/CD workflows",
    author="mruthyunjaya-lakkappanavar",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.115.0,<1.0.0",
        "uvicorn[standard]>=0.34.0,<1.0.0",
    ],
    extras_require={
        "dev": [
            "flake8>=7.0.0,<8.0.0",
            "pytest>=8.0.0,<10.0.0",
            "httpx>=0.27.0,<1.0.0",
        ],
    },
    python_requires=">=3.11",
)
