from setuptools import setup, find_packages

setup(
    name="campaign-automation",
    version="0.1.0",
    description="AI-powered campaign asset generation for social ad campaigns",
    long_description="Campaign Automation Pipeline - Generate social media ad variants using DALL-E 3, computer vision, and brand compliance validation.",
    author="Shawn Becker",
    url="https://github.com/sbecker11/campaign-automation",
    packages=find_packages(),
    install_requires=[
        'click>=8.1.7',
        'pyyaml>=6.0.1',
        'python-dotenv>=1.0.0',
        'Pillow>=10.1.0',
        'opencv-python>=4.8.1',
        'openai>=1.3.0',
        'boto3>=1.29.0',
        'requests>=2.31.0',
        'tqdm>=4.66.1',
        'scikit-image>=0.22.0',
        'numpy>=1.24.0',
        'colorama>=0.4.6',
        'rich>=13.7.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.4.3',
            'pytest-cov>=4.1.0',
            'black>=23.12.0',
            'flake8>=6.1.0',
        ]
    },
)
