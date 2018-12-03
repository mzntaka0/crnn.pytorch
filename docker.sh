sudo nvidia-docker run --ipc=host -it --name crnn -v `pwd`:/home/ -v /HDD/:/strage/ --rm nvcr.io/nvidia/pytorch:18.05-py3
