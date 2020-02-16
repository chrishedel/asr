#!/usr/bin/env python3
import os
import tarfile
import tqdm
import urllib
import urllib.request

URL = 'http://download.tensorflow.org/data/speech_commands_v0.02.tar.gz'
DIR = './dataset/small/'
OUT_FILE = DIR + 'speech_commands.tar.gz'

class TqdmUpTo(tqdm.tqdm):
  '''
  Refer to:
  https://github.com/tqdm/tqdm/blob/master/examples/tqdm_wget.py
  '''
  def update_to(self, b=1, bsize=1, tsize=None):
    if tsize is not None:
      self.total = tsize
    self.update(b * bsize - self.n)


def build_dataset():
  if not os.path.exists(DIR):
    os.makedirs(DIR)

  print('Downloading {}'.format(f))
  f = URL.replace('/', ' ').split()[-1]
  with TqdmUpTo(unit='B',
                unit_scale=True,
                unit_divisor=1024,
                miniters=1,
                desc=f) as t:
    urllib.request.urlretrieve(URL,
                               filename=OUT_FILE,
                               reporthook=t.update_to,
                               data=None)
  print('Extracting...')
  with tarfile.open(OUT_FILE) as tf:
    tf.extractall(path=DIR)

  
if __name__ == "__main__":
  build_dataset()

