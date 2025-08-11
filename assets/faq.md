1. pytorch3d installation fails\
   Download source code and compile

```bash
git clone https://github.com/facebookresearch/pytorch3d.git
python setup.py install
```

2. websocket connection error\
   Modify python/site-packages/flask\_sockets.py

```python
self.url_map.add(Rule(rule, endpoint=f)) change to 
self.url_map.add(Rule(rule, endpoint=f, websocket=True))
```

3. protobuf version too high

```bash
pip uninstall protobuf
pip install protobuf==3.20.1
```

4. Digital human doesn't blink\
Add the following steps when training the model

> Obtain AU45 for eyes blinking.\
> Run FeatureExtraction in OpenFace, rename and move the output CSV file to data/\<ID>/au.csv.

Copy au.csv to the data directory of this project

5. Add background image to digital human

```bash
python app.py --bg_img bc.jpg
```

6. Dimension mismatch error when using self-trained model\
Use wav2vec to extract audio features when training the model

```bash
python main.py data/ --workspace workspace/ -O --iters 100000 --asr_model cpierse/wav2vec2-large-xlsr-53-esperanto
```

7. ffmpeg version issue when rtmp streaming
Online feedback suggests version 4.2.2 is needed. I'm not sure which specific versions don't work. The principle is to run ffmpeg and check if the printed information contains libx264, if not it definitely won't work
```
--enable-libx264
```
8. Replace with self-trained model
```python
.
├── data
│   ├── data_kf.json (corresponds to transforms_train.json in training data)
│   ├── au.csv			
│   ├── pretrained
│   └── └── ngp_kf.pth (corresponds to trained model ngp_ep00xx.pth)

```


Other references
https://github.com/lipku/metahuman-stream/issues/43#issuecomment-2008930101


