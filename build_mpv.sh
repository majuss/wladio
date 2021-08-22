# all debs have to be allready installed

git clone https://github.com/mpv-player/mpv

cd mpv
git checkout master
 ./bootstrap.py
./waf configure --enable-libmpv-shared
./waf build --enable-libmpv-shared
sudo ./waf install --enable-libmpv-shared
