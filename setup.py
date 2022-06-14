from setuptools import setup

requirements = open("requirements.txt", "r").readlines()


setup(
    name="geocoder_module",
    version="0.2.3",
    description="Geocoder module",
    python_requires=">=3.7.6",
    url="https://github.com/lifebit-ai/nlp-geocode-module/",
    author="ML Team | Lifebit",
    packages=["geocoder_module", "logger"],
    package_data={"geocoder_module": ["*.json", "*.txt"]},
    inclued_package_data=True,
    install_requires=requirements,
)
