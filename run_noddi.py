#!/usr/bin/env python

import spams
import amico
import argparse
import os
import textwrap

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter,
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
parser.add_argument('--b0-threshold', help='Any b-value below this is considered to be b=0', type=str, default=10)

args = parser.parse_args()

study_dir = args.study_dir
subject_dir = args.subject_dir

# input and output paths bound to container already
# ae = amico.Evaluation('Study01', 'Subject01')
ae = amico.Evaluation(study_dir, subject_dir)

amico.util.fsl2scheme(f'{study_dir}/{subject_dir}/DWI.bval', f'{study_dir}/{subject_dir}/DWI.bvec')

ae.load_data(dwi_filename = 'DWI.nii.gz', scheme_filename = 'DWI.scheme', mask_filename = 'MASK.nii.gz', b0_thr = args.b0_threshold)

ae.set_model('NODDI')

ae.generate_kernels()
ae.load_kernels()
ae.fit()
ae.save_results()