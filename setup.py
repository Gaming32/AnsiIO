import setuptools

# with open('README.md') as fp:
#     long_description = fp.read()
long_description = None

setuptools.setup(
    name = 'AnsiIO',
    version = '0.2.0',
    url = 'https://github.com/gaming32/AnsiIO',
    author = 'Gaming32',
    author_email = 'gaming32i64@gmail.com',
    license = 'License :: OSI Approved :: MIT License',
    description = 'Library for doing stuff with ansi escapes',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    install_requires = [

    ],
    py_modules = [
        'ansiio',
    ],
)