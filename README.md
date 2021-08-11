<h1> Jupyter_notebooks </h1>
Up to date notebooks for all projects.

Start notebook server in correct folder with
<p>&emsp;&emsp;&emsp;jupyter-notebook </p>
  
Use the arguments below to make it available on a browser served by the host at port 8889
<p>&emsp;&emsp;&emsp;jupyter-notebook --no-browser --ip='*'</p>

access using
<p>&emsp;&emsp;&emsp;http://<b>ip</b>:8889/?token=<b>hex_code</b></p>
where <b>ip</b> is the address of the notebook server machine, and <b>hex_code</b> is provided on the server's startup stdout.

### Jupyter deployment
JupyterHub is deployed to **Jasmin:jupyter_web_test** where user login identities need to be created by the admin user (see Shared\Administration\IT\03_VMs_loging_servers.xlsx for current users). It is accessible using http://assimiladata.com
<p>A Jupyter auto-spawn service is deployed on a Google VM at http://35.242.186.132:8000/. No authentication is required.</p>
<p>All notebooks require DQTools embedded in the repository - see the notes for how this is done and how to update. They also require an identity file for DQTools to use: this is stored as .assimila_dq.txt in the home directory.... <i>(TODO need to add details here...)
</i></p>

<h3>Jupyter notebook information</h3> 
This is in Shared\Projects\2016-042 IPP PRISE\ then

05/08/01_google_cloud_deployment
* startup instructions
* notebooks

05/08/02_Deployment_Log_<latest>
* section 19 - JupyterHub installation and setup (likely requires review/update)
	
05/07
* 03_Using the Assimila Jupyter Notebook Hub (requires update)
