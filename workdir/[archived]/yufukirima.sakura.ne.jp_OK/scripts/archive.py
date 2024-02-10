import os
import zipfile
from zipfile import ZipFile
from tqdm import tqdm


def archive():
    save_path = '../saves/posts'
    zip_path = '../saves/posts_archive.zip'
    with ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipp:
        for post in tqdm(os.listdir(save_path)):
            for img in os.listdir(os.path.join(save_path, post, 'subs')):
                img_path = os.path.join(save_path, post, 'subs', img, img)
                if not os.path.exists(img_path+'.png') and not os.path.exists(img_path+'.jpg'):
                    assert False, f"{post}, {img}"
                if os.path.exists(img_path+'.png'):
                    zipp.write(img_path+'.png', arcname=os.path.join(post, img+'.png'))
                if os.path.exists(img_path+'.jpg'):
                    zipp.write(img_path+'.jpg', arcname=os.path.join(post, img+'.jpg'))

archive()