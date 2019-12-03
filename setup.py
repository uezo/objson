from setuptools import setup, find_packages

with open("./objson/version.py") as f:
    exec(f.read())

setup(
    name="objson-py",
    version=__version__,
    url="https://github.com/uezo/objson",
    author="uezo",
    author_email="uezo@uezo.net",
    maintainer="uezo",
    maintainer_email="uezo@uezo.net",
    description="objson is a object serializer that enables you to convert object <-> json/dict",
    packages=find_packages(exclude=["examples*", "develop*", "tests*"]),
    install_requires=[],
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3"
    ]
)
