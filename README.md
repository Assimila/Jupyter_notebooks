# Jupyter Notebooks #
Up to date notebooks for all projects.
## Development setup ##
### Install Anaconda ###
- For Linux machines, run the following command to download conda:\
&nbsp;&nbsp;&nbsp;&nbsp;``` wget https://repo.continuum.io/archive/Anaconda3-2018.12-Linux-x86_64.sh ```
- Next install conda with:\
&nbsp;&nbsp;&nbsp;&nbsp;``` bash Anaconda3-2018.12-Linux-x86_64.sh ```

### Clone this repository ###
	git clone https://github.com/Assimila/Jupyter_notebooks.git 

### Create environment and install packages ###
- Navigate to the ```env``` folder in the cloned repo and run the command:\
&nbsp;&nbsp;&nbsp;&nbsp;```conda create --name <env-name> --file req1.1.txt```
where ```<env-name>``` is replaced by your choice of environment name.

- To activate the environment, run:\
&nbsp;&nbsp;&nbsp;&nbsp;```conda activate <env-name> ```

### Start the notebook server ###
- Navigate into the ```Notebooks``` folder and start the server (if running on your local machine) by running the following command:\
&nbsp;&nbsp;&nbsp;&nbsp;```jupyter-notebook```
  
- If running the server remotely (e.g. on a virtual machine), use the arguments below to make it available on a browser served by the host at port 8888:\
&nbsp;&nbsp;&nbsp;&nbsp;```jupyter-notebook --no-browser --ip='*' ```

access using\
&nbsp;&nbsp;&nbsp;&nbsp;```http://<ip>:8888/?token=<hex_code>```
where __\<ip>__ is the address of the notebook server machine, and __<hex_code>__ is provided on the server's startup stdout.

## Jupyter deployment ##
JupyterHub is deployed to **Jasmin:jupyter_web_test** where user login identities need to be created by the admin user (see Shared\Administration\IT\03_VMs_loging_servers.xlsx for current users). It is accessible using http://assimiladata.com
<p>A Jupyter auto-spawn service is deployed on a Google VM at http://35.242.186.132:8000/. No authentication is required.</p>
<p>All notebooks require DQTools embedded in the repository - see the notes for how this is done and how to update. They also require an identity file for DQTools to use: this is stored as assimila_dq.txt in the user's home directory which will be called /home/jupyter_< user >. The user must be created by an admin and then sent their login name. Once they have logged in and set their password, the identity file is then uploaded from an email sent to the user using the interface's UPLOAD button. Finally, they will need to use the link sent to them to clone the code - this is all detailed in 05/07/03.<i>
</i></p>

### JupyterHub environment ###
Please read the notes in the env/ sub-directory. The environment required for deployment is not the same as that for development.
Of course, you will need to copy the required environment file across from the repository. This is most easily done via scp from another VM which has an up to date working copy.
The default port for listening is 80, but apache may be using it, in which case it is possible to change the Hub listening port on your server:

&nbsp;&nbsp;&nbsp;&nbsp;```sudo tljh-config set http.port <new_port>```

&nbsp;&nbsp;&nbsp;&nbsp;```sudo tljh-config reload proxy```

&nbsp;&nbsp;&nbsp;&nbsp;```sudo tljh-config reload hub```

## Jupyter notebook information ##
This is in Shared\Projects\2016-042 IPP PRISE\ then

05/08/01_google_cloud_deployment
* startup instructions
* notebooks

05/08/02_Deployment_Log_<latest>
* section 19 - JupyterHub installation and setup (likely requires review/update)
	
05/07
* 03_Using the Assimila Jupyter Notebook Hub (requires update)
