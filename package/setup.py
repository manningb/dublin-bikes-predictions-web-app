import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dublinbikes_harvester", # Replace with your own username
    version="0.0.1",
    author="Brian Manning",
    author_email="brian.manning@ucdconnect.ie",
    description="A package to harvest data from the Dublin Bikes API and store it in a database",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/manningb/dublin_bikes",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
