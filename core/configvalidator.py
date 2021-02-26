import logging

from schema import Schema, SchemaError


schema = Schema({
    'bot': {
        'prefix': str,
        'presence': str
    },

    'server': {
        'id': int,

        'roles': {
            'student': int,
            'mod':  int,
            'admin': int,
            'gamer': int,
            'gast': int
        },

        'channels': {
            'admin_calendar': int
        },

        'hm_feed': {
            'url': str,
            'channel': int
        },

        'semesters': {
            int: {
                'channel': int,
                'groups': {
                    str: int
                }
            }
        }
    }
})


def validate(config):
    """Makes sure the passed configuration file is valid"""
    try:
        return schema.validate(config)
    except SchemaError as e:
        logging.warning('The configuration file seems to be invalid:\n' + str(e))
