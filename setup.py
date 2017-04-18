from distutils.core import setup
#import py2exe

setup(
    name='mssql2jdl',
    version='0.01',
    packages=[''],
    url='',
    license='BSD',
    author='Aleksey Soloviov',
    author_email='lelkaklel@gmail.com',
    description='Creates JHipster JDL for MS SQL database',
    # console=[{"script": "mssql2jdl.py"}],
    # options={
                # "py2exe": {
                            # 'bundle_files': 3,
                            # 'compressed': True,
                            # "includes": ["sqlalchemy", "pyodbc", "sqlalchemy.sql.default_comparator"],
                            # "dll_excludes": [
                                # "api-ms-win-core-heap-l2-1-0.dll",
                                # "api-ms-win-core-delayload-l1-1-1.dll",
                                # "api-ms-win-core-libraryloader-l1-2-0.dll",
                                # "api-ms-win-security-activedirectoryclient-l1-1-0.dll"
                            # ],
                # }
    # },
    # zipfile=None,
    scripts=['mssql2jdl.py'],
    install_requires=[
        'sqlalchemy',
        'pyodbc'
    ]
)
