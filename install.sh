#!/bin/bash
echo $PATH

VENV=scenarios
PYVER=3.5

# Is conda installed?
conda=$(which conda)
if [ ! "$conda" ] ; then
    wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh \
        -O miniconda.sh;
    bash miniconda.sh -f -b -p $HOME/miniconda
    export PATH="$HOME/miniconda/bin:$PATH"
fi

conda update -q -y conda
conda config --prepend channels conda-forge
conda config --append channels digitalglobe # for rasterio v 1.0a9
conda config --append channels ioos # for rasterio v 1.0a2

unamestr=`uname`
if [[ "$unamestr" == 'Linux' ]]; then
    DEPARRAY=(numpy=1.11 scipy=0.19.1 matplotlib=2.0.2 rasterio=1.0a2 \
        pandas=0.20.3 h5py=2.7.0 gdal=2.1.4 pytest=3.2.0 pytest-cov=2.5.1 \
        cartopy=0.15.1 fiona=1.7.8 numexpr=2.6.2 configobj=5.0.6 \
        decorator=4.1.2 versioneer==0.18 git=2.13.3)
elif [[ "$unamestr" == 'FreeBSD' ]] || [[ "$unamestr" == 'Darwin' ]]; then
    DEPARRAY=(numpy=1.13.1 scipy=0.19.1 matplotlib=2.0.2 rasterio=1.0a9 \
        pandas=0.20.3 h5py=2.7.0 gdal=2.1.4 pytest=3.2.0 pytest-cov=2.5.1 \
        cartopy=0.15.1 fiona=1.7.8 numexpr=2.6.2 configobj=5.0.6 \
        decorator=4.1.2 versioneer==0.18)
fi
# NOTE: I added git to the linux deps list beacuse the ancient version on
#       Scientific Linux (on Atlas) causes errors.


# Is the Travis flag set?
travis=0
while getopts t FLAG; do
  case $FLAG in
    t)
      travis=1
      ;;
  esac
done
if [ $travis == 0 ] ; then
    DEPARRAY+=(ipython=6.1.0 spyder=3.2.1 jupyter=1.0.0 seaborn=0.8.0 \
        sphinx=1.6.3)
fi

# turn off whatever other virtual environment user might be in
source deactivate

# remove any previous virtual environments called pager
CWD=`pwd`
cd $HOME;
conda remove --name $VENV --all -y
cd $CWD

# Create a conda virtual environment
echo "Creating the $VENV virtual environment"
echo "with the following dependencies:"
echo ${DEPARRAY[*]}
conda create --name $VENV -y python=$PYVER ${DEPARRAY[*]}

# Activate the new environment
echo "Activating the $VENV virtual environment"
source activate $VENV

# OpenQuake v2.5.0
echo "Downloading OpenQuake v2.5.0..."
curl --max-time 60 --retry 3 -L \
    https://github.com/gem/oq-engine/archive/v2.5.0.zip -o openquake.zip
pip -q install --no-deps openquake.zip
rm openquake.zip

# MapIO and impact-utils
echo "Installing MapIO..."
pip -q install https://github.com/usgs/MapIO/archive/master.zip
echo "Installing impact-utils..."
pip -q install \
    https://github.com/usgs/earthquake-impact-utils/archive/master.zip

# Shakelib
echo "Installing shakelib..."
pip -q install https://github.com/usgs/shakelib/archive/master.zip

# Shakemap
echo "Installing shakemap..."
pip -q install https://github.com/usgs/shakemap/archive/master.zip

# Install shakemap-scearios
echo "Installing shakemap..."
pip install -e .

# tell the user they have to activate this environment
echo "Type 'source activate scenarios' to use this new virtual environment."
