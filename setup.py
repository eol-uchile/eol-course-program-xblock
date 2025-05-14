"""Setup for eolcourseprogram XBlock."""

from __future__ import absolute_import

import os

from setuptools import setup, find_packages


def package_data(pkg, roots):
    """Generic function to find package_data.

    All of the files under each of the `roots` will be declared as package
    data for package `pkg`.

    """
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


setup(
    name='eolcourseprogram-xblock',
    version='0.2.0',
    author="Oficina EOL UChile",
    author_email="eol-ing@uchile.cl",
    description='XBlock and API to show and manage course programs in the Open edX',
    license='AGPL v3',
    packages=find_packages(),
    install_requires=[
        'XBlock',
    ],
    entry_points={
        'xblock.v1': [
            'eolcourseprogram = eolcourseprogram:EolCourseProgramXBlock',
        ],
        "lms.djangoapp": [
            "eolcourseprogram = eolcourseprogram.apps:EolCourseProgramConfig",
        ],
        "cms.djangoapp": [
            "eolcourseprogram = eolcourseprogram.apps:EolCourseProgramConfig",
        ]
    },
    package_data=package_data("eolcourseprogram", ["static", "public"]),
)
