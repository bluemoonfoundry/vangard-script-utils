"""
Setup configuration for vangard-script-utils package.
"""
from setuptools import setup, find_packages
import os

# Read the version from vangard/__init__.py
def get_version():
    init_path = os.path.join(os.path.dirname(__file__), 'vangard', '__init__.py')
    with open(init_path, 'r') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return "0.0.0"

# Read the README for long description
def get_long_description():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

setup(
    name="vangard-script-utils",
    version=get_version(),
    author="Vangard Team",
    description="A command-line interface and automation toolkit for DAZ Studio",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/vangard-script-utils",  # Update with actual URL
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data={
        'vangard': ['scripts/*.dsa'],
    },
    include_package_data=True,
    install_requires=[
        'PyYAML>=6.0',
        'fastapi>=0.85.0',
        'uvicorn[standard]>=0.18.3',
        'prompt-toolkit>=3.0.0',
        'python-dotenv>=1.0.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'pytest-mock>=3.10.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'vangard=vangard.main:main',
            'vangard-cli=vangard.cli:main',
            'vangard-interactive=vangard.interactive:main',
            'vangard-server=vangard.server:main',
            'vangard-gui=vangard.gui:main',
        ],
    },
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    keywords='daz-studio automation cli 3d-graphics',
)
