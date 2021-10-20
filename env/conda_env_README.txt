Conda environment README file.

The environment used to develop notebooks, specifically the enhanced features of COP26 demo, required significant package additions. If using a straight-forward local jupyter notebook server, then req1.1.txt is sufficient to host the notebook and all its features.

However, the notebooks are deployed on an installation of TLJH on the public server and for this, many conflicts occur when attempting to install the new packages via the command line. After much investigation, it was found that a requirements file could be installed on the base environment once that had been stripped of all later additions. The last hurdle was to include the packages to spawn a new server for a user for which updates were required.
The resulting *1.2* environment files are the output of a working TLJH environment.

conda_env_1.2.yaml
- created with command:
    sudo /opt/tljh/user/bin/conda env export  -n base > /home/assimila/conda_env_1.2.yaml
- contains yaml format of all package versions including their specific build version

conda_env_1.2_no_builds.yaml
- created with command:
    sudo /opt/tljh/user/bin/conda env export --no-builds -n base > /home/assimila/conda_env_1.2_no_builds.yaml
- contains yaml format of all package versions

conda_env_1.2_explicit.txt
- created with command:
    sudo /opt/tljh/user/bin/conda list --explicit > /home/assimila/conda_env_1.2_explicit.txt
- contains txt format of all package versions including their conda repository url and specific build version


Useful commands (all pre-pended with 'sudo /opt/tljh/user/bin/')
conda list --revisions
    shows which packages were installed and when
conda install -c conda-forge --revision 0
    strips all later additions and takes it back to the unaltered first installation; channel argument needed for this operation as it may not have been in the default list
conda install --file requirements.txt
    reads the requirements file and installs into the current environment
conda install async_generator
    required for spawning servers on the Hub; updates ca-certs, certificates and conda
conda activate base
    ensure the base environment is current

jupyter troubleshoot > ~/log.txt
    excellent output of all the inner machinations