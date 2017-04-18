#!/usr/bin/env python
# -*-coding:utf-8-*-
"""
SYNOPSIS

    mssql2jdl [-h,--help] [-v,--verbose] [--version]
    Execute mssql2jdl --help for detailed description.

DESCRIPTION

    Creates JHipster JDL file for MS SQL Server database.

EXAMPLES

    mssql2jdl -h
    Print help and exit

AUTHOR

    Aleksey Soloviov <lelkaklel@gmail.com>

CREATED

    2017.04.17

COPYRIGHT

    (C) Aleksey Soloviov <lelkaklel@gmail.com> 2017.04.17

VERSION

    1.0

REQUIREMENTS

    Python version: >= 3.6

EXIT STATUS

    0 - Successful execution
    1 - Unknown error
"""

import os
import sys
import re
import traceback
import argparse
import time
import logging
import types

from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import mapper, sessionmaker
#from urllib.parse import quote_plus
from sqlalchemy.sql import sqltypes
from sqlalchemy.dialects.mssql import base as sqltypes_base

TYPES = {
    sqltypes.INTEGER: 'Integer',
    sqltypes.BIGINT: 'Integer',
    sqltypes.SMALLINT: 'Integer',
    sqltypes.NUMERIC: 'BigDecimal',
    sqltypes.BOOLEAN: 'Boolean',
    sqltypes.CHAR: 'String',
    sqltypes.NCHAR: 'String',
    sqltypes.VARCHAR: 'String',
    sqltypes.NVARCHAR: 'String',
    sqltypes.DATE: 'LocalDate',
    sqltypes.DATETIME: 'ZonedDateTime',
    sqltypes.BINARY: 'Blob',
    sqltypes_base.BIT: 'Boolean',
    sqltypes_base.TINYINT: 'Integer',
    sqltypes_base.DATETIME2: 'ZonedDateTime',
    sqltypes.DECIMAL: 'Decimal',
    sqltypes.FLOAT: 'Decimal'
}


# logging config
logging.basicConfig(filename='mssql2jdl.log',
                    format='[%(asctime)s] %(levelname)-8s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
                    level=logging.WARNING)
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
# set a format which is simpler for console use
formatter = logging.Formatter('%(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
log = logging.getLogger('')
log.addHandler(console)


def normalize_name(orig_name):
    return ''.join([x.capitalize() for x in orig_name.split('_')])


def main(params):
    engine = create_engine('mssql+pyodbc://{user}:{password}@{dsn}'.format(user=params.username, password=params.password, dsn=params.dsn))
    metadata = MetaData(engine)

    foreign_keys = []

    for table_name in engine.table_names():
        tab = Table(table_name, metadata, autoload=True)
        table_norm_name = normalize_name(tab.name)
        print('')
        print('entity {}{} {{ // table "{}"'.format(params.tableprefix, table_norm_name, tab.name))
        keys = tab.columns.keys()
        for key in keys:
            val = tab.columns[key]
            jdl_type = TYPES.get(type(val.type), '<not found>')
            required_text = ' required' if val.nullable else ''
            length = ''
            if hasattr(val.type, 'length'):
                if type(val.type) == sqltypes.NUMERIC:
                    jdl_type = 'Integer'
                length = ' maxlength({})'.format(val.type.length)
            comma = ',' if key != keys[-1:][0] else ''
            if val.foreign_keys:
                foreign_keys.append(dict(table_name=table_name, table_norm_name=table_norm_name, column=val.copy(),
                                         foreign_table=list(val.foreign_keys)[0].column.table.name,
                                         foreign_column=list(val.foreign_keys)[0].column.name))
            print('    {} {}{}{}{} // {}'.format(key, jdl_type, length, required_text, comma, str(val.type).lower()))
        print('}')

    if foreign_keys:
        for relation in foreign_keys:
            print('')
            print('relationship OneToMany { ')
            foreign_table_norm_name = normalize_name(relation['foreign_table'])
            comma = ''  # '',' if relation != foreign_keys[-1:][0] else ''
            print('    {}{} to {}{}{{{}}}{}'.format(params.tableprefix, foreign_table_norm_name, params.tableprefix,
                                                    relation['table_norm_name'], relation['foreign_table'].lower(),
                                                    comma))
            print('} ')



if __name__ == '__main__':
    try:
        start_time = time.time()
        t = re.compile('^DESCRIPTION[^\w]+([\s\S]*)^EXAMPLES', re.IGNORECASE | re.MULTILINE)
        descr = t.findall(globals()['__doc__'])[0]
        parser = argparse.ArgumentParser(description=descr)
        parser.add_argument('-v', '--verbose', action='store_true', default=False, help='verbose output')
        parser.add_argument('-p', '--tableprefix', action='store', default='', help='table name prefix')
        parser.add_argument('dsn', help='DSN name')
        parser.add_argument('username', help='SQL Server user name')
        parser.add_argument('password', help='SQL Server user password')
        if len(sys.argv) == 1:
            parser.print_help()
            sys.exit(2)
        params = parser.parse_args()
        if params.verbose:
            log.setLevel(logging.DEBUG)
        # if len(args) < 1:
        #    parser.error ('missing argument')
        log.info('{:=^60}'.format('START'))
        log.debug('OPTIONS:')
        for i in dir(params):
            if i.startswith('_') or isinstance(getattr(params, i), types.MethodType):
                continue
            log.debug('    {: <15} : {}'.format(i, getattr(params, i)))
        main(params)
        log.info('TOTAL TIME IN MINUTES: {:.2f}'.format((time.time() - start_time) / 60.0)),
        log.info('{:=^60}'.format('END'))
        sys.exit(0)
    except KeyboardInterrupt as e:  # Ctrl-C
        raise e
    except SystemExit as e:  # sys.exit()
        raise e
    except Exception as e:
        log.critical('ERROR, UNEXPECTED EXCEPTION')
        log.critical(str(e))
        traceback.print_exc()
        os._exit(1)
