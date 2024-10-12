from setuptools import find_packages, setup

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().split("\n")

setup(
    name="BeatMatch",
    version="0.0.1",
    install_requires=requirements,
    packages=find_packages(),
    entry_points={
            'console_scripts': [
                'beatmatch = beatmatch.entrypoints:main',
            ]
    }
)
