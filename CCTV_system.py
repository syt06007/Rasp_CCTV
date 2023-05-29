import RPi.GPIO as GPIO
import time
import cv2

sensor_GPIO = 7
buzzer_GPIO = 18

GPIO.setmode(GPIO.BCM)

GPIO.setup(buzzer_GPIO, GPIO.OUT)
GPIO.setup(sensor_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
start_sensor_t = time.time()
# def my_callback_rising(channel):

#     GPIO.output(buzzer_GPIO, True) # Buzzer
#     print('sensor detect motion!')
#     time.sleep(0.1)
#     GPIO.output(buzzer_GPIO, False)

def my_callback_both(channel):
    print('sensor time : ', start_sensor_t - time.time())
    # Sensor RISING Edge
    if GPIO.input(sensor_GPIO): 
                
        print('motion detected!!')
        start_cam_t = time.time()
        # 얼굴인식 classifier
        faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        
        # cv2 동영상 출력
        cap = cv2.VideoCapture(0) # 0번째 카메라 이용
        cap.set(3,640) # set Width
        cap.set(4,480) # set Height

        # cv2를 이용한 동영상 녹화 객체 생성 (VideoWriter)
        rec_file_name = time.strftime('%Y-%m-%d %H:%M:%S')
        w = round(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(rec_file_name+'.avi', fourcc, fps, (w,h))
        
        while True:
            ret, img = cap.read()
            img = cv2.flip(img, -1) # 상하반전
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.2,
                minNeighbors=5,
                minSize=(20, 20)
            )
            out.write(img)
            for (x,y,w,h) in faces:
                cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = img[y:y+h, x:x+w]
                print('-------WARNING :: HUMAN-------')
                print('camera time :', start_cam_t - time.time())

                GPIO.output(buzzer_GPIO, True)
            cv2.imshow('video',img) # video라는 이름으로 출력
            k = cv2.waitKey(30) & 0xff

            if not GPIO.input(sensor_GPIO):
                print('motion disappeared')
                cap.release()
                out.release()
                cv2.destroyAllWindows()

    # FALLING Edge
    else :
        print('motion disappeared...')
        GPIO.output(buzzer_GPIO, False)
        cap.release()
        out.release()
        cv2.destroyAllWindows()

# RISING : motion detected / FALLING : motion disappeared

GPIO.add_event_detect(sensor_GPIO, GPIO.BOTH, callback = my_callback_both)


try :
    while 1:
        print('.')
        time.sleep(0.1)
finally:
    GPIO.cleanup()
    print('GPIO cleanup')