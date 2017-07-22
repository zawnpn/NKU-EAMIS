from setuptools import setup, find_packages
 
with open('README.md') as f:
    long_description = f.read()
 
setup(
    name = 'nkueamis',
    version = '0.4.2',
    author = 'Wanpeng Zhang',
    author_email = 'zawnpn@gmail.com',
    keywords = ('NKU', 'eamis', 'Education'),
    long_description=long_description,
    url = 'https://github.com/zawnpn/nkueamis',
    description = 'A simple tool to help get information in NKU-EAMIS(NKU Education Affairs Management Information System).',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
      ],
    license = 'MIT',
    packages = find_packages(),
    install_requires=['docopt', 'requests', 'bs4', 'prettytable'],
    entry_points={
        'console_scripts':[
            'nkueamis=nkueamis.nkueamis:main'
        ]
      },
)
