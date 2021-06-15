#!/usr/bin/env python

import argparse
import multiprocessing
import numpy as np
import os
import textwrap

# Diffusivity values for the model
# https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0217118

# Parallel diffusivity, reduce for neonates / GM
dPar = 1.7E-3

# isotropic diffusion
dIso = 3.0E-3

# IC parameters are discretized, these defaults from AMICO, designed to reproduce NODDI toolbox
# These are not user accessible for now
IC_VFs = np.linspace(0.1,0.99,12)
IC_ODs = np.hstack((np.array([0.03, 0.06]),np.linspace(0.09,0.99,10)))

# If ex-vivo is true, a "dot" compartment is added (immobile water, see https://doi.org/10.1016/j.neuroimage.2011.09.081)
isExvivo  = False

# custom formatter, using both default display and raw text description
class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass

parser = argparse.ArgumentParser(
    formatter_class=CustomFormatter,
    description=textwrap.dedent('''\
        Runs the AMICO NODDI fit. Expects data organized as
        study_dir/
                 subject_dir/
                            DWI.nii.gz  (DWI data)
                            DWI.bvec    (FSL bvecs)
                            DWI.bval    (FSL bvals)
                            MASK.nii.gz (Binary brain mask)

        Because AMICO pre-computes its basis kernels for each imaging scheme, it's best to make
        a self-contained study directory for each scan. However, you can save some time by
        organizing multiple sessions under the same study_dir, but only if they all have the
        same imaging scheme. Minor variation due to motion correction or residual gradient
        errors are acceptable.

        Output will be written to

        study_dir/
                subject_dir/
                            AMICO/
                                NODDI/
                                    FIT_ICVF.nii.gz
                                    FIT_ISOVF.nii.gz
                                    FIT_OD.nii.gz
                                    FIT_dir.nii.gz
                                    config.pickle
        '''))

parser.add_argument('--study-dir', help='Absolute path to base data directory', type=str)
parser.add_argument('--subject-dir', help='Subject directory under study_dir', type=str)
parser.add_argument('--b0-threshold', help='Any b-value below this is considered to be b=0', type=float, default=10)
parser.add_argument('--ex-vivo', help='Flag for ex-vivo data. Adds an additional compartment to the model. It may also \
    be advisable to change the diffusivity options.', action="store_true")
parser.add_argument('--csf-diffusivity', help='CSF compartment diffusivity in mm^2/s.', type=float, default=dIso)
parser.add_argument('--num-threads', help='Maximum number of threads to use, set to 0 to not limit threads', type=int, default=0)
parser.add_argument('--parallel-diffusivity', help='Intracellular diffusivity parallel to neurites, in mm^2/s. \
    Default is appropriate for adult WM', type=float, default=dPar)


args = parser.parse_args()

study_dir = args.study_dir
subject_dir = args.subject_dir
num_threads = args.num_threads

dPar = args.parallel_diffusivity
dIso = args.csf_diffusivity
isExvivo = args.ex_vivo

# Print out model params
print(textwrap.dedent(
    f'''
    --- Fit parameters ---
    b0 threshold         :   {args.b0_threshold}
    CSF diffusivity      :   {dIso}
    Parallel diffusivity :   {dPar}
    Ex vivo              :   {isExvivo}
    '''
    ))

# Threading environment variables must be set before importing amico
# We set these to 1 and control threads within AMICO, this makes CPU usage
# better track the maximum number of threads
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'

import amico

# input and output paths bound to container already
# ae = amico.Evaluation('Study01', 'Subject01')
ae = amico.Evaluation(study_dir, subject_dir)

amico.util.fsl2scheme(f'{study_dir}/{subject_dir}/DWI.bval', f'{study_dir}/{subject_dir}/DWI.bvec')

ae.load_data(dwi_filename = 'DWI.nii.gz', scheme_filename = 'DWI.scheme', mask_filename = 'MASK.nii.gz', b0_thr = args.b0_threshold)

ae.set_model('NODDI')

ae.model.set(dPar, dIso, IC_VFs, IC_ODs, isExvivo)

if (num_threads > 0):
    ae.CONFIG['solver_params']['numThreads'] = num_threads
else:
    ae.CONFIG['solver_params']['numThreads'] = multiprocessing.cpu_count()

ae.generate_kernels()
ae.load_kernels()
ae.fit()
ae.save_results()