from setuptools import setup
try:
    import multiprocessing
except ImportError:
    pass

setup(
    name='httpie-akamai',
    description='Akamai utility plugins for HTTPie.',
    long_description=open('README.rst').read().strip(),
    version='0.1.1',
    author='Matt Eckhaus',
    author_email='matt@eckha.us',
    license='BSD',
    url='https://github.com/matteck/httpie-akamai',
    download_url='https://github.com/matteck/httpie-akamai',
    py_modules=['httpie_akamai'],
    zip_safe=False,
    entry_points={
        'httpie.plugins.formatter.v1': [
            'httpie_akamai = httpie_akamai:AkamaiFormatterPlugin'
        ],
        'httpie.plugins.transport.v1': [
            'httpie_akamai_transport = httpie_akamai:AkamaiTransportPlugin'
        ]
    },
    install_requires=[
        'httpie>=0.9.0',
        'requests',
        'urlparse3'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'Environment :: Plugins',
        'License :: OSI Approved :: BSD License',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Utilities'
    ]
)
