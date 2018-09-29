import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages


# Get the version
from example_web_app import __version__


def get_long_description():
    readme = ""

    with open('README.md', encoding='utf-8') as readme_file:
        readme = readme_file.read()

    return readme


REQUIREMENTS_FOLDER = os.getenv('REQUIREMENTS_PATH', '')
requirements = [line.strip() for line in open(os.path.join(REQUIREMENTS_FOLDER, "requirements.txt"), 'r')]
test_requirements = [line.strip() for line in open(os.path.join(REQUIREMENTS_FOLDER, "requirements_dev.txt"), 'r')]


setup(
    name='example_web_app',
    version='{version}'.format(version=__version__),
    description="AN Example Web API project powered by Aiohttp and SQLAlchemy",
    long_description=get_long_description(),
    author="Ahmad Alhour",
    author_email='me@aalhour.com',
    url='example.com/api/v1.0',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "example_web_app": [
            "docs/*",
            "templates/*",
            "static/*",
            "static/js/*",
            "static/css/*",
        ]
    },
    install_requires=requirements,
    zip_safe=False,
    keywords="example_web_app",
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
            'run_example_web_app=example_web_app.app:run_app',
            'init_example=example_web_app.init_example:init_example'
        ]
    }
)
