'''Dejar aquí toda aquellas librerías necesarias en el proyecto.
Script generado por CDK'''
import setuptools


with open("README.md", encoding="utf-8") as fp:
    long_description = fp.read()


setuptools.setup(
    name="mlops_skeleton",
    version="0.0.1",

    description="An empty CDK Python app",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"": "mlops_skeleton"},
    packages=setuptools.find_packages(where="mlops_skeleton"),

    install_requires=[
        "aws-cdk.core==1.119.0",
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
