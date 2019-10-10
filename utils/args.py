# If you edit this file, please consider updating bids-app-template

import subprocess as sp
import os, os.path as op
import logging
import re
import shutil
import json

from .fs_license import find_freesurfer_license

log = logging.getLogger(__name__)


def make_file_name_safe(input_basename, replace_str=''):
    """
    removes non-safe characters from a filename and returns a filename with these characters replaced with replace_str
    :param input_basename: the input basename of the file to be replaced
    :type input_basename: str
    :param log: a logger instance
    :type log: logging.Logger
    :param replace_str: the string with which to replace the unsafe characters
    :type   replace_str: str
    :return: output_basename, a safe
    :rtype: str
    """
    import re
    safe_patt = re.compile('[^A-Za-z0-9_\.]+')
    # if the replacement is not a string or not safe, set replace_str to x
    if not isinstance(replace_str, str) or safe_patt.match(replace_str):
        log.warning('{} is not a safe string, removing instead'.format(replace_str))
        replace_str = ''
    if replace_str:
        log.debug('Replacing unsafe characters with {}'.format(replace_str))
    # Replace non-alphanumeric (or underscore) characters with replace_str
    safe_output_basename = re.sub(safe_patt, replace_str, input_basename)

    return safe_output_basename


def get_inputs_and_args(context):
    """
    Process inputs, contextual values and build a dictionary of
    key:value command-line parameter names:values These will be
    validated and assembled into a command-line below.  
    """

    # 1) Process Inputs

    # editme: optional.  Keep this if the gear runs Freesurfer.  This is here
    # because one way to pass the license is by an input
    find_freesurfer_license(context, '/opt/freesurfer/license.txt')

    # 2) Process Contextual values
    # e.g. context.matlab_license_code

    # 3) Process Configuration (config, rest of command-line parameters)
    config = context.config
    params = {}
    for key in config.keys():
        if key[:5] == 'gear-':  # Skip any gear- parameters
            continue
        # Use only those boolean values that are True
        if type(config[key]) == bool:
            if config[key]:
                params[key] = True
            # else ignore (could this cause a problem?)
        else:
            if len(key) == 1:
                params[key] = config[key]
            else:
                if config[key] != 0:  # if zero, skip and use defaults
                    params[key] = config[key]
                # else ignore (could this caus a problem?)
    
        context.gear_dict['param_list'] =  params


def validate(context):
    """
    Validate settings of the Parameters constructed.
    Gives warnings for possible settings that could result in bad results.
    Gives errors (and raises exceptions) for settings that are violations 
    """
    param_list = context.gear_dict['param_list']
    # Test for input existence
    # if not op.exists(params['i']):
    #    raise Exception('Input File Not Found')

    # Tests for specific problems/interactions that can raise exceptions or log warnings
    # if ('betfparam' in params) and ('nononlinreg' in params):
    #    if(params['betfparam']>0.0):
    #        raise Exception('For betfparam values > zero, nonlinear registration is required.')

    # if ('s' in params.keys()):
    #    if params['s']==0:
    #        log.warning(' The value of ' + str(params['s'] + \
    #                    ' for -s may cause a singular matrix'))


def build_command(context):
    """
    command is a list of prepared commands
    param_list is a dictionary of key:value pairs to be put into the command list
    as such ("-k value" or "--key=value")
    """

    command = context.gear_dict['command']

    param_list = context.gear_dict['param_list']

    for key in param_list.keys():
        # Single character command-line parameters are preceded by a single '-'
        if len(key) == 1:
            command.append('-' + key)
            if len(str(param_list[key])) != 0:
                # append it like '-k value'
                command.append(str(param_list[key]))
        # Multi-Character command-line parameters are preceded by a double '--'
        else:
            # If Param is boolean and true include, else exclude
            if type(param_list[key]) == bool:
                if param_list[key]:
                    command.append('--' + key)
            else:
                # If Param not boolean, but without value include without value
                if len(str(param_list[key])) == 0:
                    # append it like '--key'
                    command.append('--' + key)
                else:
                    # check for argparse nargs='*' lists of multiple values so
                    #  append it like '--key val1 val2 ...'
                    if (isinstance(param_list[key], str) and len(param_list[key].split()) > 1):
                    # then it is a list of multiple things: e.g. "--modality T1w T2w"
                        command.append('--' + key)
                        for item in param_list[key].split():
                            command.append(item)
                    else: # single value so append it like '--key=value'
                        command.append('--' + key + '=' + str(param_list[key]))
        if key == 'verbose':
            # handle a 'count' argparse argument where manifest gives
            # enumerated possibilities like v, vv, or vvv
            # e.g. replace "--verbose=vvv' with '-vvv'
            command[-1] = '-' + param_list[key]

    log.info('Command: ' + ' '.join(command))

    return command


# vi:set autoindent ts=4 sw=4 expandtab : See Vim, :help 'modeline'
