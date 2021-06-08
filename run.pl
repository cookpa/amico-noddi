#!/usr/bin/perl -w
#
# Wrapper script for calling run_noddi.py
#
#

use strict;
use File::Path qw(make_path);
use File::Spec;
use File::Basename;
use Getopt::Long;

my $numThreads = 1;
my $workingDir = "";

my $usage = qq{
  $0
      --dwi-root
      --output-root
      [ options ]

  Required args:
   --brain-mask
     Brain mask image in ".nii.gz" format.
   --dwi-root
     DWI data root, where the data is root.[nii.gz, bval, bvec].
   --output-root
     Path and file root prepended onto output files.

  Options:

   --num-threads
     Maximum number of CPU threads to use. This will be used to set environment variables limiting threads
     for OMP and MKL (default = ${numThreads}). Set to 0 to bypass this step and rely on software defaults.

   --work-dir
     Temp directory to copy source data and do processing. Defaults to a directory created at run time under
     /tmp.

  Output:
   Output is organized under the specified output directory.


  AMICO site: https://github.com/daducci/AMICO


  Citations:

  Please include citations for the NODDI method (Zhang et al) implemented in AMICO (Daducci et al).

  Zhang H, Schneider T, Wheeler-Kingshott CA, Alexander DC.
  NODDI: practical in vivo neurite orientation dispersion and density imaging of the human brain.
  NeuroImage. 2012 Jul 16;61(4):1000-16. doi: 10.1016/j.neuroimage.2012.03.072. PMID: 22484410.

  Daducci A, Canales-Rodríguez EJ, Zhang H, Dyrby TB, Alexander DC, Thiran JP.
  Accelerated Microstructure Imaging via Convex Optimization (AMICO) from diffusion MRI data.
  Neuroimage. 2015 Jan 15;105:32-44. doi: 10.1016/j.neuroimage.2014.10.026. PMID: 25462697.

};


if ($#ARGV < 0) {
    print $usage;
    exit 1;
}

# Required args
my ($brainMask, $dwiRoot, $outputRoot);

# Parse args
GetOptions("dwi-root=s" => \$dwiRoot,
           "brain-mask=s" => \$brainMask,
           "num-threads=i" => \$numThreads,
           "output-root=s" => \$outputRoot,
           "work-dir=s" => \$workingDir
          )
    or die("Error in command line arguments\n");


# Derive subject label from input, used to create sandboxed data
my ($dwiFileRoot, $dwiDir) = fileparse($dwiRoot);

my $subjectLabel = $dwiFileRoot;

# working temp dir - this is a temp dir, unless overridden by the user
if (! -d ${workingDir}) {
    $workingDir = `mktemp --tmpdir -d amicoNODDI.XXXXXXXX.tmpdir`;
    chomp($workingDir);
    (-d ${workingDir}) or die("Could not create working dir $workingDir");
}

my $workingSubjectDir = "${workingDir}/${subjectLabel}";

make_path("$workingSubjectDir");

foreach my $inputExt ("nii.gz", "bval", "bvec") {
    (-f "${dwiRoot}.${inputExt}") or die "\nCannot find required input: ${dwiRoot}.${inputExt}\n";

    # Copy data to sandboxed input dir
    system("cp ${dwiRoot}.${inputExt} ${workingSubjectDir}/DWI.${inputExt}");
}

(-f $brainMask) or die("\nCannot find brain mask: $brainMask\n");
system("cp ${brainMask} ${workingSubjectDir}/MASK.nii.gz");

if ($numThreads == 0) {
    print "Maximum number of threads not set\n";
}
else {
    $ENV{'OMP_NUM_THREADS'} = $numThreads;
    $ENV{'MKL_NUM_THREADS'} = $numThreads;
}

my ($outputFileRoot, $outputDir) = fileparse($outputRoot);

if (! -d $outputDir) {
    make_path("$outputDir");
}

my $amicoExit = system("/opt/scripts/run_noddi.py --study-dir ${workingDir} --subject-dir ${subjectLabel}");

# Copy output to output root
my @outputFileNames = qw(FIT_ICVF.nii.gz FIT_OD.nii.gz FIT_ISOVF.nii.gz FIT_dir.nii.gz config.pickle);

foreach my $outputFileName (@outputFileNames) {
    my $outputFile = "${workingSubjectDir}/AMICO/NODDI/$outputFileName";
    if (-f $outputFile) {
        system("cp $outputFile ${outputRoot}$outputFileName");
    }
    else {
        print "ERROR: Missing expected output file $outputFileName - processing may have errors\n";
    }
}

exit($amicoExit >> 8);
