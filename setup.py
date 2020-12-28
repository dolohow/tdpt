import setuptools


def get_requirements():
    """Build the requirements list for this project"""
    requirements_list = []

    with open('requirements.txt') as requirements:
        for install in requirements:
            requirements_list.append(install.strip())

    return requirements_list


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tdpt",
    version="1.3",
    author="dolohow",
    author_email="lukasz@zarnowiecki.pl",
    description="Torrent downloading progress on Telegram",
    entry_points={
        'console_scripts': ['tdpt = tdpt:__main__.main'],
    },
    install_requires=get_requirements(),
    keywords="telegram bot transmission liveupdates torrents rtorrent torrent",
    long_description_content_type="text/markdown",
    long_description=long_description,
    url="https://github.com/dolohow/tdpt",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
