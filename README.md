# Tello Control App with GUI

This app is designed to control Tello drone from PC / laptop over WiFi connection and view the camera video. It can be run both on Linux and Windows computers.

##  Installation
Before running ensure that the following python libraries are present in your system:
- tello-python
- opencv
- pillow

Tello-python installation (Windows)

```bash
>> git clone https://github.com/harleylara/tello-python.git
>> cd tello-python
>> python setup.py install `
```
Tello-python installation (Linux)

```bash
>> git clone https://github.com/harleylara/tello-python.git
>> cd tello-python
>> sudo python setup.py install `
```
Opencv installation
```bash
conda install -c conda-forge opencv 
```
or
```bash
pip install opencv-python
```

Pillow installation
```bash
conda install -c conda-forge pillow
```
or
```bash
pip install Pillow
```
#### !!Important!!
On Windows PCs check firewall settings for TCP and UDP port blocking.