import cv2
import numpy as np
import time
import screen

'''

-----AD-SOYAD : ÖMER EROĞLU-------
-----TARİH : 13:03:2024-------
**** Yazılım  projemde kapasitörlerin üretim hatlarında ki hatalarını analiz etmek amaçlanmakta. 
Bu kapasitörün bacakları arasındaki mesafe aşağıdaki verilen şartlara göre piksel cinsinden ölçülmektedir.*******

->Bu betikte, bir görüntü üzerinde yer alan kapasitörün bacakları arasındaki mesafe piksel cinsinden ölçülmektedir. 
Bu ölçüm, kapasitörün bacaklarının en alt noktasından başlayarak 20 piksel yukarıda bulunan bir noktadan itibaren 
ve ayrıca bacakların orta noktası hesaplanarak gerçekleştirilir.

->Öncelikle, görüntü üzerinde ROI alanı ayrılır.Bilateral Blur ve Canny yöntemleri uygulanarak kenarlar belirginleştirilir ve konturlar bulunur. 
Bilateral Blur, görüntü üzerindeki gürültüyü azaltırken kenarları korur. 
Canny yöntemi ise kenarları tespit etmek için oldukça etkili bir yöntemdir.

->Kenarların belirlendiği piksel koordinatları 'coordinatesOfEdges' dizisinde saklanır.
->find_point' fonksiyonu kullanılarak, kondansatörün sol ve sağ bacaklarında istenilen noktaların koordinatları belirlenir. 
Bu noktalar, sol ve sağ bacakların en alt kısmından 20 piksel yukarıda bulunan orta noktalarıdır.
->find_distance' fonksiyonu, bu noktalar arasındaki mesafeyi piksel cinsinden hesaplar ve sonucu döndürür.
'''


def mesafe_bul(point1, point2):
    # İki nokta arasındaki öklidyen mesafeyi hesaplar. son mesafe algılama safhası

    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    dsquared = dx ** 2 + dy ** 2
    result = dsquared ** 0.5
    return result


def merkez_bul(contours):
    # Verilen konturların merkezini bulur.
    centroidCoordinates = []
    for (i, cnt) in enumerate(contours):
        cent_moment = cv2.moments(cnt)
        centroid_x = int(cent_moment['m10'] / cent_moment['m00'])
        centroid_y = int(cent_moment['m01'] / cent_moment['m00'])
        centroidCoordinates.append([centroid_x, centroid_y])
    return centroidCoordinates


def orta_nokta_bul(point1, point2):
    # Verilen iki noktanın orta noktasını hesaplar.
    centerpointCoordinates = (int((point1[0] + point2[0]) * 0.5), int((point1[1] + point2[1]) * 0.5))
    return centerpointCoordinates


def nokta_bul(contours, coordinatesOfEdges):
    # Verilen konturların ve kenarların koordinatlarıyla, kapasitör bacaklarındaki noktaları bulur.
    centroidCoordinates = merkez_bul(contours)
    if len(contours) == 1:
        centroidCoordinates = (centroidCoordinates[0][0], centroidCoordinates[0][1])
    elif len(contours) == 2:
        centroidCoordinates = orta_nokta_bul(centroidCoordinates[0], centroidCoordinates[1])

    indexes_x_left = np.where(coordinatesOfEdges[1] < centroidCoordinates[0])[0]
    indexes_x_right = np.where(coordinatesOfEdges[1] >= centroidCoordinates[0])[0]

    max_y_coordinate_of_left = np.amax(coordinatesOfEdges[0][indexes_x_left])
    midpoint_y_coordinate_of_left_leg = max_y_coordinate_of_left - 20
    x_indexes_of_midpoint_y_coordinate_of_left_leg = np.where(coordinatesOfEdges[0] ==
                                                              midpoint_y_coordinate_of_left_leg)[0]
    x_coord_left = []
    for i in range(len(x_indexes_of_midpoint_y_coordinate_of_left_leg)):
        if coordinatesOfEdges[1][x_indexes_of_midpoint_y_coordinate_of_left_leg[i]] < centroidCoordinates[0]:
            x_coord_left.append(coordinatesOfEdges[1][x_indexes_of_midpoint_y_coordinate_of_left_leg[i]])
    midpoint_x_coordinate_of_left_leg = int((x_coord_left[0] + x_coord_left[1]) / 2)

    max_y_coordinate_of_right = np.amax(coordinatesOfEdges[0][indexes_x_right])
    midpoint_y_coordinate_of_right_leg = max_y_coordinate_of_right - 20
    x_indexes_of_midpoint_y_coordinate_of_right_leg = np.where(coordinatesOfEdges[0] ==
                                                               midpoint_y_coordinate_of_right_leg)[0]
    x_coord_right = []
    for i in range(len(x_indexes_of_midpoint_y_coordinate_of_right_leg)):
        if coordinatesOfEdges[1][x_indexes_of_midpoint_y_coordinate_of_right_leg[i]] >= centroidCoordinates[0]:
            x_coord_right.append(coordinatesOfEdges[1][x_indexes_of_midpoint_y_coordinate_of_right_leg[i]])
    midpoint_x_coordinate_of_right_leg = int((x_coord_right[0] + x_coord_right[1]) / 2)

    return [midpoint_x_coordinate_of_left_leg, midpoint_y_coordinate_of_left_leg], \
        [midpoint_x_coordinate_of_right_leg, midpoint_y_coordinate_of_right_leg]


def baslatma(img_yolu=None):
    # Verilen görüntü dosyasından kapasitör bacakları arasındaki mesafeyi hesaplar.
    img = cv2.imread(img_yolu)

    distance = 0
    totalRuntime = 0

    start_time = time.time()

    # ROI (Region of Interest) koordinatlarını belirleme
    roix1 = 0
    roiy1 = 480
    roix2 = 1650
    roiy2 = 680

    # ROI'yi belirleme- analiz edilecek bölge seçildi
    ROI = img[roiy1:roiy2, roix1:roix2]

    # bilateral kullanılması sebebi kenarları daha net gösterdiği ve görüntüyü yumuşattığı için
    bilateralSmoothing = cv2.bilateralFilter(ROI, 9, 75, 75) # (9,75,75 değeri alt seviyelerdir ve deneme yanılma ile bulundu)

    # Kenarları bulma (keskin kenarlar ve gürültü açısından etkili olduğu için cannykullanıldı)
    edges = cv2.Canny(bilateralSmoothing, 100, 200)

    # Kenarların koordinatlarını bulma(0 olmayan değerleri array a atar)
    coordinatesOfEdges = np.nonzero(edges)

    # Contourları bulma (birbirine kapalı şekiller 1 konturdur)
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # Kapasitör bacaklarındaki noktaları bulma
    leftLegPoint, rightLegPoint = nokta_bul(contours, coordinatesOfEdges) #fonksiyona gönderiyoruz

    # Kapasitör bacakları arasındaki mesafeyi hesaplama
    distance = mesafe_bul(leftLegPoint, rightLegPoint)  # fonksiyona gönderip ar. mesafeyi alıyoruz

    print("Kapasitör bacakları arasındaki mesafe(piksel):", distance)

    # Kapasitör bacakları arasındaki orta noktanın bulunması
    midpoint_between_capacitor_legs = orta_nokta_bul(leftLegPoint, rightLegPoint)

    # ROI'ye noktaları, çizgiyi ve mesafeyi ekleyerek görselleştirilmesi
    cv2.line(img, (0, 480), (1650, 480), (0,255, 0), 2)
    cv2.line(img, (0, 680), (1650, 680), (0, 255, 0), 2)

    cv2.circle(ROI, (leftLegPoint[0], leftLegPoint[1]), radius=5, color=(0, 255, 0), thickness=-1)
    cv2.circle(ROI, (rightLegPoint[0], rightLegPoint[1]), radius=5, color=(0, 255, 0), thickness=-1)

    cv2.line(ROI, (leftLegPoint[0], leftLegPoint[1]), (rightLegPoint[0], rightLegPoint[1]), (0, 255, 0), 4)

    cv2.putText(ROI, "distance=" + str(distance),(midpoint_between_capacitor_legs[0] - 170, midpoint_between_capacitor_legs[1] - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)

    # ROI'yi ana görüntüye yerleştirilmesi
    img[roiy1:roiy2, roix1:roix2] = ROI

    # Çıktı görüntüsünü kaydedilmesi ( bu şekilde screen arayzümüzde bu görüntüyü açabilmekteyiz)
    cv2.imwrite("output_image.jpg", img)

    # işlem süresi hesaplamaları....
    end_time = time.time()

    totalRuntime = end_time - start_time

    print("Program çalışma süresi(sn):", totalRuntime, "saniye")

    # Toplam çalışma süresi ve kapasitör bacakları arasındaki mesafeyi döndürme
    return totalRuntime, distance, img


'''
    #görüntüleme araçları (her işlem adımı aşağıda istenirse görüntülenebilmektedir)
    
    cv2.imshow("ROI",ROI)
    cv2.imshow("kapasitor",img)
    cv2.imshow("bilateral",bilateralSmoothing)
    cv2.imshow("canny",edges)

    cv2.waitKey(0)
    cv2.destroyAllWindows()

baslatma()
'''
