#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --time=1:00:00
#SBATCH --mem=8GB
#SBATCH --gres=gpu
#SBATCH --job-name=test_habitat
#SBATCH --mail-type=END
#SBATCH --mail-user=ky2288@nyu.edu

module purge

singularity exec --nv \
	    --bind /usr/share/glvnd/egl_vendor.d/10_nvidia.json \
	    --overlay /scratch/ky2288/overlay-10GB-400K.ext3:ro \
	    /scratch/work/public/singularity/cuda11.2.2-cudnn8-devel-ubuntu20.04.sif \
	    /bin/bash -c "source /ext3/env.sh; conda activate /ext3/python-habitat; python /scratch/ky2288/spatial-reasoning/dataset/examples/example.py --depth_sensor --save_png --scene data/scene_datasets/habitat-test-scenes/skokloster-castle.glb"
