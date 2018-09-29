import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages


# Get the version
from {{cookiecutter.app_name}} import __version__


def get_long_description():
    readme = ""

    with open('README.md', encoding='utf-8') as readme_file:
        readme = readme_file.read()

    return readme


REQUIREMENTS_FOLDER = os.getenv('REQUIREMENTS_PATH', '')
requirements = [line.strip() for line in open(os.path.join(REQUIREMENTS_FOLDER, "requirements.txt"), 'r')]
test_requirements = [line.strip() for line in open(os.path.join(REQUIREMENTS_FOLDER, "requirements_dev.txt"), 'r')]


setup(
    name='{{cookiecutter.app_name}}',
    version='{version}'.format(version=__version__),
    description="{{cookiecutter.project_short_description}}",
    long_description=get_long_description(),
    author="{{cookiecutter.author_name}}",
    author_email='{{cookiecutter.author_email}}',
    url='{{cookiecutter.project_website}}',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "{{cookiecutter.app_name}}": [
            "docs/*",
            "templates/*",
            "static/*",
            "static/js/*",
            "static/css/*",
        ]
    },
    install_requires=requirements,
    zip_safe=False,
    keywords="{{cookiecutter.app_name}}",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    entry_points={
        'console_scripts': [
            'run_{{cookiecutter.app_name}}={{cookiecutter.app_name}}.app:run_app',
            'init_example={{cookiecutter.app_name}}.init_example:init_example'
        ]
    }
)
