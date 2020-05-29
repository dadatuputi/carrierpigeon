from distutils.core import setup

setup(name='CarrierPigeon',
        version='1.0',
        description='Email-based message service for kids and their loved ones',
        author='Bradford Law',
        url='',
        entry_points={'console_scripts': ['carrierpigeon = carrierpigeon.__main__:main']},
        install_requires=[
            'pyttsx3',
            'IMAPClient',
            'python-vlc',
            'python-dateutil',
            'gpiozero',
            'RPi.GPIO',
            'pyaudio',
            'fysom',
            ],
        )
