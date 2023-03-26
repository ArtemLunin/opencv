import cv2
from PIL import Image, ImageChops, ImageStat, ImageFilter
#import difflib

#Функция вычисления хэша
def CalcImageHash(FileName):
    image = cv2.imread(FileName) #Прочитаем картинку
    resized = cv2.resize(image, (8,8), interpolation = cv2.INTER_AREA) #Уменьшим картинку
    gray_image = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY) #Переведем в черно-белый формат
    avg=gray_image.mean() #Среднее значение пикселя
    ret, threshold_image = cv2.threshold(gray_image, avg, 255, 0) #Бинаризация по порогу
    
    #Рассчитаем хэш
    _hash=""
    for x in range(8):
        for y in range(8):
            val=threshold_image[x,y]
            if val==255:
                _hash=_hash+"1"
            else:
                _hash=_hash+"0"
            
    return _hash

def CompareHash(hash1,hash2):
    l = len(hash1)
    i = 0
    count = 0
    while i<l:
        if hash1[i] != hash2[i]:
            count = count+1
        i = i+1
    return count


def CompareIimages(images):
    image1 = Image.open(images[0]).convert("L").filter(ImageFilter.DETAIL)
    image2 = Image.open(images[1]).convert("L").filter(ImageFilter.DETAIL)
    print(image1.mode)
    print(image2.mode)
    result = ImageChops.difference(image1, image2)
    image1.show('image1')
    image2.show('image2')
    result.show()
    # print(result.getbbox())
    stat = ImageStat.Stat(result)
    diff_ratio = sum(stat.mean) / (len(stat.mean) * 255)
    return diff_ratio * 100
