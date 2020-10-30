# -*- coding: utf-8 -*-
"""Command line scripts to launch a `Pw2wannier90Calculation` for testing and demonstration purposes.

This launcher assumes that the SEED and the PREFIX used in the previous PW calculation (parent_folder) are the same as
those hardcoded in the Pw2wannier90Calculation class. We also hardcode some parameters and options.
"""
import click

from aiida.cmdline.params import options as options_core
from aiida.cmdline.params import types
from aiida.cmdline.params.options import OverridableOption
from aiida.cmdline.utils import decorators

from ..utils import launch
from ..utils import options
from . import cmd_launch

NNKP_FILE = OverridableOption(
    '-S',
    '--nnkp-file',
    type=types.NodeParamType(sub_classes=('aiida.data:singlefile',)),
    required=True,
    help='SinglefileData containing the .nnkp file generated by a wannier90.x preprocessing.'
)

SCDM_MODE = OverridableOption(
    '--scdm-mode',
    type=click.Choice(['no', 'isolated', 'erfc', 'gaussian']),
    default='no',
    show_default=True,
    help='Whether to use the SCDM algorithm to determine the UNK matrices.'
)

WRITE_UNK = OverridableOption(
    '-u',
    '--write-unk',
    is_flag=True,
    default=False,
    show_default=True,
    help='Output also the UNK matrices (for real-space plotting of the Wannier functions).'
)


@cmd_launch.command('pw2wannier90')
@options_core.CODE(required=True, type=types.CodeParamType(entry_point='quantumespresso.pw2wannier90'))
@options.PARENT_FOLDER(required=True, help='RemoteData node containing the output of a PW NSCF calculation.')
@NNKP_FILE()
@SCDM_MODE()
@WRITE_UNK()
@options.MAX_NUM_MACHINES()
@options.MAX_WALLCLOCK_SECONDS()
@options.WITH_MPI()
@options.DAEMON()
@decorators.with_dbenv()
def launch_calculation(
    code, parent_folder, nnkp_file, scdm_mode, write_unk, max_num_machines, max_wallclock_seconds, with_mpi, daemon
):
    """Run a Pw2wannier90Calculation with some sample parameters and the provided inputs."""
    from aiida.orm import Dict
    from aiida.plugins import CalculationFactory
    from aiida_quantumespresso.utils.resources import get_default_options

    parameters = {
        'INPUTPP': {
            'write_amn': True,
            'write_mmn': True,
        }
    }

    parameters['INPUTPP']['write_unk'] = write_unk

    if scdm_mode != 'no':
        parameters['INPUTPP']['scdm_proj'] = True
        parameters['INPUTPP']['scdm_entanglement'] = scdm_mode

    # In this command-line example, we always retrieve .amn, .mmn and .eig,
    # but we never retrieve the UNK files that are big
    settings = {'ADDITIONAL_RETRIEVE_LIST': ['*.amn', '*.mmn', '*.eig']}

    inputs = {
        'code': code,
        'parent_folder': parent_folder,
        'nnkp_file': nnkp_file,
        'parameters': Dict(dict=parameters),
        'settings': Dict(dict=settings),
        'metadata': {
            'options': get_default_options(max_num_machines, max_wallclock_seconds, with_mpi),
        }
    }

    launch.launch_process(CalculationFactory('quantumespresso.pw2wannier90'), daemon, **inputs)
