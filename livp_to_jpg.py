import os
from PIL import Image
import shutil
import zipfile
from tqdm import tqdm
import pillow_heif

def livp_to_jpg(img_item,img_source,livp_to_jpg_dir):
    img_id = img_item.split('.')[0]
    livp_zip_name = os.path.join(livp_to_jpg_dir,img_id+'.zip')

    copy_file(img_source, livp_zip_name)#将文件复制成zip归档的形式

    heic_name = ''
    heic_on = 0
    with zipfile.ZipFile(livp_zip_name) as zf:
        for zip_file_item in zf.namelist():
            if zip_file_item.split('.')[-1]=='heic': #处理heic的照片
                zf.extract(zip_file_item, livp_to_jpg_dir)
                heic_name = zip_file_item
                heic_on = 1
            else: #处理视频  或者  非heic文件（某些时候回产生jpg）
                type = '.' + zip_file_item.split('.')[-1]
                zf.extract(zip_file_item, livp_to_jpg_dir)
                mov_name = zip_file_item
                old_name = os.path.join(livp_to_jpg_dir,mov_name)
                new_name = os.path.join(livp_to_jpg_dir,img_id + type)
                os.rename(old_name,new_name)


    os.remove(livp_zip_name)#delete the zip file

    try:
        if heic_on == 1:
            heic_img_path = os.path.join(livp_to_jpg_dir,heic_name)

            heif_file = pillow_heif.read_heif(heic_img_path)
            image = Image.frombytes(
                heif_file.mode,
                heif_file.size,
                heif_file.data.tobytes(),
                "raw",
            )

            jpg_save_path = os.path.join(livp_to_jpg_dir, img_id + '.jpg')
            image.save(jpg_save_path, format="jpeg")

            os.remove(heic_img_path)  # delete the heic file

    except Exception as e: #大疆pocket3的livp会解压产生伪heic文件，无法用库打开，可直接改后缀为jpg查看（电脑端有时候不改也可以）
        old_name = os.path.join(livp_to_jpg_dir,heic_name)
        new_name = os.path.join(livp_to_jpg_dir, img_id + '.jpg')
        os.rename(old_name,new_name)

def heic_to_jpg(img_item,img_source,livp_to_jpg_dir):
    img_id = img_item.split('.')[0]
    heif_file = pillow_heif.read_heif(img_source)
    image = Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        "raw",
    )

    jpg_save_path = os.path.join(livp_to_jpg_dir, img_id + '.jpg')
    image.save(jpg_save_path, format="jpeg")

    heic_path = os.path.join(livp_to_jpg_dir, img_id + '.heic')

if __name__ == '__main__':

    livp_dir = r'D:\1'
    livp_to_jpg_dir = r'D:\1' #目标文件夹，支持与上述相同，为覆盖替换，若不同，则原文件夹不动

    img_list = os.listdir(livp_dir)

    for img_item in tqdm(img_list):
        if img_item.split('.')[-1]=='livp': #livp文件进行拆包处理（jpg图片＋mov视频）
            print(img_item)
            img_source = os.path.join(livp_dir,img_item)
            img_destination = os.path.join(livp_to_jpg_dir,img_item)
            livp_to_jpg(img_item, img_source, livp_to_jpg_dir)
            if livp_dir == livp_to_jpg_dir:
                os.remove(img_source)
        elif img_item.split('.')[-1]=='heic': #heic文件进行jpg处理
            print(img_item)
            img_source = os.path.join(livp_dir,img_item)
            img_destination = os.path.join(livp_to_jpg_dir,img_item)
            heic_to_jpg(img_item, img_source, livp_to_jpg_dir)
            if livp_dir == livp_to_jpg_dir:
                os.remove(img_source)
        else: #其余文件原封不动导入
            if livp_dir == livp_to_jpg_dir:
                continue
            original_path = os.path.join(livp_dir,img_item)
            destination_path = os.path.join(livp_to_jpg_dir,img_item)
            shutil.copy2(original_path, destination_path)
            
