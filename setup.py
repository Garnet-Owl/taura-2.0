"""
A minimal setup.py file to make the package installable with pip.
Not needed when using Poetry, but included for compatibility.
"""

from setuptools import setup

if __name__ == "__main__":
    setup(
        name="taura",
        version="2.0.0",
        description="Machine translation model for translating Kikuyu to English",
        packages=["app"],
        python_requires=">=3.8",
    )
