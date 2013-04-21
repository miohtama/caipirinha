import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

requires = ['pyramid', 'WebError', 'pymongo', 'mongoengine', 'irc', 'pyzmq', 'pyramid_webassets', 'ipdb', 'logutils']

setup(name='caipirinha',
      version='0.0',
      description='caipirinha',
      long_description=README,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author="Mikko Ohtamaa",
      author_email='mikko@opensourcehacker.com',
      url='https://github.com/miohtama',
      keywords='web pyramid pylons mongodb',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="caipirinha",
      entry_points="""\
      [paste.app_factory]
      main = caipirinha:main

      [console_scripts]
      caipirinha-bot = caipirinha.bot.core:main
      """,
      paster_plugins=['pyramid'],
      )
