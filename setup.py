import setuptools


with open("README.md", 'r') as readme:
    long_description = readme.read()

setuptools.setup(
    name="simple-plugin-loader-mammo0",
    version="1.0",
    author="Marc Ammon",
    author_email="marc.ammon@hotmail.de",
    description="Dynamically load other python modules to your project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mammo0/py-simple-plugin-loader",
    packages=["simple_plugin_loader"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL-3.0 License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)
