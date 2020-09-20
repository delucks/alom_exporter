from setuptools import setup

test_require = ['pytest']

with open('requirements.txt') as f:
    reqs = [l.strip() for l in f if not any(l.startswith(t) for t in test_require)]

with open('README.md', 'r') as f:
    long_desc = f.read()

version = "0.0.5"

setup(
    name='alom_exporter',
    description='Prometheus exporter for Sun ALOM statistics',
    long_description=long_desc,
    long_description_content_type="text/markdown",
    version=version,
    install_requires=reqs,
    tests_require=test_require,
    packages=['alom'],
    py_modules=[],
    entry_points={
        'console_scripts': [
            'alom_exporter = alom.metrics:main'
        ]
    },
    python_requires='>=3.6',
    author='delucks',
    author_email='me@jamieluck.com',
    license='GPLv3',
    url='https://github.com/delucks/alom_exporter',
    download_url=f'https://github.com/delucks/alom_exporter/tarball/{version}',
    keywords=['prometheus', 'sun', 'oracle', 'sparc', 'alom', 'prometheus exporter'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Operating System :: POSIX :: BSD',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities'
    ]
)
