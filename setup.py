from setuptools import setup

setup(
    name="8bit-wallpaper",
    version="0.0.0",
    requires=['pywapi'],
    py_modules=['8bitday'],
    entry_points={
        "console_scripts": [
            '8bitday = 8bitday:main'
        ]
    }

)
