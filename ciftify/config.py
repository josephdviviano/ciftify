#!/usr/bin/env python
"""
These functions search the environment for software dependencies and configuration.
"""

import os
import subprocess
import multiprocessing as mp
import logging

def find_workbench():
    """
    Returns path of the workbench bin/ folder, or None if unavailable.
    """
    try:
        workbench = subprocess.check_output('which wb_command', shell=True)
    except:
        workbench = None

    return workbench

def find_fsl():
    """
    Returns the path of the fsl bin/ folder, or None if unavailable.
    """
    try:
        dir_fsl = subprocess.check_output('which fsl', shell=True)
        dir_fsl = '/'.join(dir_fsl.split('/')[:-1])
    except:
        dir_fsl = None

    return dir_fsl

def find_freesurfer():
    """
    Returns the path of the freesurfer bin/ folder, or None if unavailable.
    """
    try:
        dir_freesurfer = subprocess.check_output('which recon-all', shell=True)
        dir_freesurfer = '/'.join(dir_freesurfer.split('/')[:-1])
    except:
        dir_freesurfer = None

    return dir_freesurfer

def find_scene_templates():
    """
    Returns the hcp scene templates path. If the shell variable
    HCP_SCENE_TEMPLATES is set, uses that. Otherwise returns the defaults
    stored in the ciftify/data/scene_templates folder.
    """
    dir_hcp_templates = os.getenv('HCP_SCENE_TEMPLATES')

    if dir_hcp_templates is None:
        ciftify_path = os.path.dirname(__file__)
        dir_hcp_templates = os.path.abspath(os.path.join(ciftify_path,
                '../data/scene_templates'))
    return dir_hcp_templates

def find_ciftify_global():
    """
    Returns the path to ciftify required config and support files. If the
    shell variable CIFTIFY_DATA is set, uses that. Otherwise returns the
    defaults stored in the ciftify/data folder.
    """
    dir_templates = os.getenv('CIFTIFY_DATA')

    if dir_templates is None:
        ciftify_path = os.path.dirname(__file__)
        dir_templates = os.path.abspath(os.path.join(ciftify_path, '../data'))

    return dir_templates

def find_HCP_S900_GroupAvg():
    """return path to HCP_S900_GroupAvg which should be in ciftify"""
    s900 = os.path.join(find_ciftify_global(), 'HCP_S900_GroupAvg_v1')
    return s900

def find_freesurfer_data():
    """
    Returns the freesurfer data path defined in the environment.
    """
    try:
        dir_freesurfer_data = os.getenv('SUBJECTS_DIR')
    except:
        dir_freesurfer_data = None

    return dir_freesurfer_data

def find_hcp_data():
    """
    Returns the freesurfer data path defined in the environment.
    """
    try:
        dir_hcp_data = os.getenv('HCP_DATA')
    except:
        dir_hcp_data = None

    return dir_hcp_data

def wb_command_version():
    '''
    Returns version info about wb_command.

    Will raise an error if wb_command is not found, since the scripts that use
    this depend heavily on wb_command and should crash anyway in such
    an unexpected situation.
    '''
    wb_path = find_workbench()
    if wb_path is None:
        raise EnvironmentError("wb_command not found. Please check that it is "
                "installed.")
    wb_help = subprocess.check_output('wb_command', shell=True)
    wb_version = wb_help.split(os.linesep)[0:3]
    sep = '{}    '.format(os.linesep)
    wb_v = sep.join(wb_version)
    all_info = 'wb_command: {}Path: {}    {}'.format(sep,wb_path,wb_v)
    return(all_info)

def freesurfer_version():
    '''
    Returns version info for freesurfer
    '''
    fs_path = find_freesurfer()
    if fs_path is None:
        raise EnvironmentError("Freesurfer cannot be found. Please check that "
            "it is installed.")
    try:
        fs_buildstamp = os.path.join(os.path.dirname(fs_path),
                'build-stamp.txt')
        with open(fs_buildstamp, "r") as text_file:
            bstamp = text_file.read()
    except:
        return "freesurfer build information not found."
    bstamp = bstamp.replace(os.linesep,'')
    info = "freesurfer:{0}Path: {1}{0}Build Stamp: {2}".format(
            '{}    '.format(os.linesep),fs_path, bstamp)
    return info

def fsl_version():
    '''
    Returns version info for FSL
    '''
    fsl_path = find_fsl()
    if fsl_path is None:
        raise EnvironmentError("FSL not found. Please check that it is "
                "installed")
    try:
        fsl_buildstamp = os.path.join(os.path.dirname(fsl_path), 'etc',
                'fslversion')
        with open(fsl_buildstamp, "r") as text_file:
            bstamp = text_file.read()
    except:
        return "FSL build information not found."
    bstamp = bstamp.replace(os.linesep,'')
    info = "FSL:{0}Path: {1}{0}Version: {2}".format('{}    '.format(os.linesep),
            fsl_path, bstamp)
    return info

def ciftify_version(file_name=None):
    '''
    Returns the path and the latest git commit number and date
    '''
    logger = logging.getLogger(__name__)

    print(__file__)

    if file_name is not None:
        try:
            dir_ciftify = subprocess.check_output('which {}'.format(file_name),
                    shell=True)
        except subprocess.CalledProcessError:
            logger.error("Cannot find ciftify file {}, finding default "
                    "version information".format(file_name))
            dir_ciftify = __file__
            file_name = None
    else:
        # Find the path to this file
        dir_ciftify = __file__

    ciftify_path = os.path.dirname(dir_ciftify)
    try:
        gitcmd = 'cd {}; git log | head'.format(ciftify_path)
        git_log = subprocess.check_output(gitcmd, shell=True)
    except subprocess.CalledProcessError:
        logger.error("Something went wrong while retrieving git log. Returning "
                "ciftify path only.")
        return "Ciftify:{0}Path: {1}".format(os.linesep, ciftify_path)

    commit_num = git_log.split(os.linesep)[0]
    commit_num = commit_num.replace('commit', 'Commit:')
    commit_date = git_log.split(os.linesep)[2]
    info = "Ciftify:{0}Path: {1}{0}{2}{0}{3}".format('{}    '.format(os.linesep),
            ciftify_path, commit_num, commit_date)

    if file_name:
        ## if a specific file is passed, returns its commit too
        try:
            gitcmd = 'cd {}; git log --follow {} | head'.format(ciftify_path,
                    file_name)
            git_log = subprocess.check_output(gitcmd, shell = True)
        except subprocess.CalledProcessError:
            logger.error("Cannot retrieve commit history for {}. Returning "
                    "ciftify commit info only.".format(file_name))
            return info
        commit_num = git_log.split(os.linesep)[0]
        commit_num = commit_num.replace('commit', 'Commit:')
        commit_date = git_log.split(os.linesep)[2]
        info = "{1}{5}Last commit for {2}:{0}{3}{0}{4}".format('{}    '.format(
                os.linesep), info, file_name, commit_num, commit_date,
                os.linesep)
    return info

def system_info():
    ''' return formatted version of the system info'''
    sys_info = os.uname()
    sep = '{}    '.format(os.linesep)
    info = "System Info:{0}OS: {1}{0}Hostname: {2}{0}Release: {3}{0}Version: " \
            "{4}{0}Machine: {5}".format(
            sep, sys_info[0], sys_info[1], sys_info[2], sys_info[3],
            sys_info[4])
    return info
