import sys
import os.path
import pandas as pd
import urllib.request
from PIL import Image

BASEWIDTH=300

if len(sys.argv) == 1:
    print('must pass in subdir')
    sys.exit(1)

if len(sys.argv) == 2:
    print('must pass in type of job, ie(validation, test, or train)')
    sys.exit(1)

subdir = sys.argv[1]
folder = sys.argv[2]

def get_image(id,url):

  ext = url.split('.')[-1]

  if ext == 'jpg' or ext == 'JPG' or ext == 'JPEG':
      ext == 'jpeg'
  file_name = subdir + '/' + folder + '/images/' + id + '.' + ext

  if os.path.isfile(file_name) == True:
      img = Image.open(file_name)
      return file_name, img.size[0], img.size[1]

  urllib.request.urlretrieve(url, file_name)
  img = Image.open(file_name)
  wpercent = (BASEWIDTH/float(img.size[0]))
  hsize = int((float(img.size[1])*float(wpercent)))
  img = img.resize((BASEWIDTH,hsize), Image.ANTIALIAS)
  img.save(file_name)
  width = img.size[0]
  height = img.size[1]
  return file_name, width, height

class_df = pd.read_csv(subdir + '/class_descriptions.csv')
images = pd.read_csv(folder + '/images.csv')
human_annotations = pd.read_csv(folder + '/annotations-human.csv')
human_bbox = pd.read_csv(folder + '/annotations-human-bbox.csv')
machine_annotations = pd.read_csv(folder + '/annotations-machine.csv')
classes_bbox = pd.read_csv('./classes-bbox.csv')
rows = []
for chunk in class_df['LabelName']:
    bboxes = human_bbox.loc[human_bbox['LabelName'] == chunk]
    if bboxes.empty == True:
        continue
    # description = class_df.loc[class_df['LabelName'] == chunk]['LabelDescription']
    # print(chunk, description.values)
    values = human_annotations.loc[human_annotations['LabelName'] == chunk]
    for value in values['ImageID']:
        image = images.loc[images['ImageID'] == value]
        bbox = human_bbox.loc[human_bbox['ImageID'] == value]
        image_values = get_image(value, image['OriginalURL'].values[0])
        file_name = image_values[0]
        width = image_values[1]
        height = image_values[2]

        if bbox.empty == True:
            continue

        xmin = bbox['XMin'].values[0]
        xmax = bbox['XMax'].values[0]
        ymin = bbox['YMin'].values[0]
        ymax = bbox['YMax'].values[0]

        row = {'filename': file_name,
               'width': width,
               'height': height,
               'class': chunk,
               'xmin': xmin,
               'xmax': xmax,
               'ymin': ymin,
               'ymax': ymax}
        print(row)
        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(subdir + '/' + folder + '/results.csv', index=False)

    values = machine_annotations.loc[machine_annotations['LabelName'] == chunk]
    for value in values['ImageID']:
        image = images.loc[images['ImageID'] == value]
        new_file = get_image('machine/' + value, image['OriginalURL'].values[0])
