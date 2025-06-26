from setuptools import setup

package_name = 'mic_reader'

setup(
    name=package_name,
    version='0.0.1',
    packages=['mic_reader_node'], 
    install_requires=['setuptools', 'sounddevice', 'numpy'],
    zip_safe=True,
    maintainer='your_name',
    maintainer_email='your@email.com',
    description='Mic reader node for UMA-16 mic array',
    license='MIT',
    entry_points={
        'console_scripts': [
            'mic_reader_node = mic_reader_node.mic_reader_node:main',
        ],
    },
)