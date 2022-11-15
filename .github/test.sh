#!/bin/dash

pip install -e /openedx/requirements/eol-course-program-xblock

cd /openedx/requirements/eol-course-program-xblock
cp /openedx/edx-platform/setup.cfg .
mkdir test_root
cd test_root/
ln -s /openedx/staticfiles .

cd /openedx/requirements/eol-course-program-xblock

DJANGO_SETTINGS_MODULE=lms.envs.test EDXAPP_TEST_MONGO_HOST=mongodb pytest eolcourseprogram/tests.py
