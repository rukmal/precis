from setuptools import find_packages, setup

# Import long description from README
with open("docs/README.md", "r", encoding="utf-8") as readme_file:
    long_description = readme_file.read()

# Import requirements from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as requirements_file:
    requirements_list = requirements_file.read().split("\n")[:-1]

setup(
    name="precis",
    version="1.5.2",
    author="Rukmal Weerawarana",
    packages=find_packages(),
    author_email="rukmal.weerawarana@gmail.com",
    description="",
    long_description=long_description,
    url="https://github.com/rukmal/precis",
    install_requires=requirements_list,
    package_data={"": ["templates/", "precis_ontology.rdf"]},
    python_requires=">=3.6"
)
