apt-get update
apt-get install -y  cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev
apt-get install -y libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libjasper-dev libdc1394-22-dev
pip install -r requirements.txt
git clone https://github.com/SeanNaren/warp-ctc.git
cd warp-ctc
mkdir build
cd build
cmake ..
make
cd ../pytorch_binding
python setup.py install
