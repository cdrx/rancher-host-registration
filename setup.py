from setuptools import setup

setup(name='rancher-agent-registration',
    version='1.2',
    description='Command line tool to register the current host with your Rancher server',
    url='https://github.com/cdrx/rancher-host-registration',
    author='Chris Rose',
    license='MIT',
    packages=['rancher_agent_registration'],
    zip_safe=False,
    install_requires=[
        'click',
        'requests',
        'colorama'
    ],
    entry_points = {
        'console_scripts': ['rancher-agent-registration=rancher_agent_registration.cli:main'],
    }
)
