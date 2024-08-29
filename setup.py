# setup.py

from setuptools import setup, find_packages

setup(
    name="omics_oracle",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "python-arango",
        "gradio",
        # Add any other dependencies here
    ],
    author="Trent Leslie",
    author_email="trent.leslie@phenomehealth.org",
    description="A biomedical query system integrating Gemini API and Spoke knowledge graph",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/omics_oracle",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)