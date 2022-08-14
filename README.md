# Spatial Reasoning

## Generate Dataset

### 1. Setting the environment
For faster installation, we want to use the computation node by running an interactivate job.
```
srun -t30:00 -c4 --mem=3000 --pty /bin/bash
```
Create a directory for the environment.
```
mkdir /scratch/$USER/environments
cd /scratch/<NetID>/environments
```
Copy the overlay images to the directory and unzip it (here we use the image that has 15GB spaces and can hold 500k files). Then rename the image
```
cp -rp /scratch/work/public/overlay-fs-ext3/overlay-15GB-500K.ext3.gz .
gunzip overlay-15GB-500K.ext3.gz
mv overlay-15GB-500K.ext3 habitat.ext3
```
Launch the Singularity container in read/write mode (with the :rw flag). 
```
singularity exec --overlay habitat.ext3:rw /scratch/work/public/singularity/cuda11.6.124-cudnn8.4.0.27-devel-ubuntu20.04.4.sif /bin/bash
```
The above starts a bash shell inside the referenced Singularity Container overlayed with the 15GB 500K you set up earlier. This creates the functional illusion of having a writable filesystem inside the typically read-only Singularity container.

Now, inside the container, download and install miniconda to /ext3/miniconda3
```
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
sh Miniconda3-latest-Linux-x86_64.sh -b -p /ext3/miniconda3
```
Next, create a wrapper script /ext3/env.sh, and open it with vim
```
touch /ext3/env.sh
vim /ext3/env.sh
```
Now you are in the interface of vim. Press `i` to change to insert mode. Copy the following text and paste it to the interface:
```
#!/bin/bash

source /ext3/miniconda3/etc/profile.d/conda.sh
export PATH=/ext3/miniconda3/bin:$PATH
export PATH=/ext3/miniconda3/envs/habitat/bin:$PATH
export PYTHONPATH=/ext3/miniconda3/bin:$PATH
export PYTHONPATH=/ext3/miniconda3/envs/habitat:$PATH
```
Press `esc` to exit insert mode. Type `:wq` to save and exit the file.

The wrapper script will activate your conda environment, to which you will be installing your packages and dependencies. 

Activate your conda environment with the following:
```
source /ext3/env.sh
```
Create a new conda environment for habitat:
```
conda create -n habitat python=3.7 cmake=3.14.0 -y
conda activate habitat
```
Install habitat sim:
```
conda install habitat-sim withbullet headless -c conda-forge -c aihabitat -y
```

Now, the environment is set up. enter `exit` twice to exit the singularity and end the interactive job.

### 2.Download the code
Download this repository:
```
cd /scratch/$USER
git clone https://github.com/Gaaaavin/spatial-reasoning.git
```

### 3. Run the code
Run an interactivate job with gpu.
```
srun -t30:00 -c4 --mem=4000 --gres=gpu:1 --pty /bin/bash
```
Enter singularity and activate the environment.
```
singularity exec --overlay /scratch/$USER/environments/habitat.ext3:ro /scratch/work/public/singularity/cuda11.6.124-cudnn8.4.0.27-devel-ubuntu20.04.4.sif /bin/bash
source /ext3/env.sh
conda activate habitat
```
Download the testing 3D scenes
```
cd /scratch/$USER/spatial-resaoning/dataset/examples
python -m habitat_sim.utils.datasets_download --uids habitat_test_scenes --data-path data
```
Excecute testing code
```
python example.py --save_png --depth_sensor --scene data/scene_datasets/habitat-test-scenes/skokloster-castle.glb
```
The agent will traverse a particular path and you should see the performance stats at the very end, something like this:
`640 x 480, total time 137.86 s, frame time 137.859 ms (7.3 FPS)`. You can find the generated images in the directory `observation`.
