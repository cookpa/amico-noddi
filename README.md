# amico-noddi

Containerized wrapper to fit NODDI with AMICO.

Inputs:
  * DWI data in the format `/path/to/dwi.[nii.gz, bvec, bval]`
  * Brain mask (.nii.gz)

Output is NODDI metrics computed via AMICO:
  * FITxICVF.nii.gz
  * FITxOD.nii.gz
  * FITxISOVF.nii.gz
  * FITxdir.nii.gz

Example usage:

```
docker run -v /tmp:/tmp -v $PWD:/data/input --rm -it amico-noddi:latest \
    --dwi-root /data/input/dwi \
    --brain-mask /data/input/brain_mask.nii.gz \
    --output-root /data/input/AMICO/AMICO_ \
    --num-threads 2
```


## Installed dependencies (see links for licensing info)

AMICO: https://github.com/daducci/AMICO

SPArse Modeling Software (SPAMS): http://spams-devel.gforge.inria.fr


## Citations

Accelerated Microstructure Imaging via Convex Optimization (AMICO) from diffusion MRI data
Alessandro Daducci, Erick Canales-Rodriguez, Hui Zhang, Tim Dyrby, Daniel C Alexander, Jean-Philippe Thiran
NeuroImage 105, pp. 32-44 (2015)

NODDI: practical in vivo neurite orientation dispersion and density imaging of the human brain
Hui Zhang, Torben Schneider, Claudia A Wheeler-Kingshott, Daniel C Alexander
NeuroImage. 16;61(4):1000-16 (2012)


