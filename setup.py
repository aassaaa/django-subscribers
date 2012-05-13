from setuptools import setup, find_packages
import os

package = 'subscribers'
setup(
    name='django-subscribers',
    version='1.0',
    description='django-subscribers is a batch mailing utility for Django',
    long_description = open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
    author='Dave Hall',
    requires = ['django (>=1.3)'],
    license = 'MIT license',

    packages = find_packages('src'),
    package_dir = {'':'src'},
    package_data = {'subscribers': [
            'templates/admin/*/*/*.html',
            'templates/subscribers/*.*',
            'locale/*/LC_MESSAGES/*',
        ],
    },

    classifiers=[
        'Development Status :: 1 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Framework :: Django',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)