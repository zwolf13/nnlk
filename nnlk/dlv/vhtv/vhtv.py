from multiprocessing import Process
import time
import nnlk.dlv.dlv as dlv

ONE_HOUR = 60.0 * 60.0


def download():
    """
    vhtv-dlv.py --realm ${REALM} --camera ${CAM} --timestamp ${TIMESTAMP} --playlist-url ${PLAYLIST_URL}
    =>
    dlv.py -c cookies\vhtv.txt -t "voyeur-house.tv/${REALM}/${CAM} - ${TIMESTAMP} - %(id)s.%(ext)s" "${URL}"
    """
    dlv._init()
    REALM = 'realm73'
    CAM = 'cam13'
    TIMESTAMP = '1669680000'
    PLAYLIST_URL = 'http://www.test.com/'

    cookie = '../cookies/vhtv.txt'
    template = f"voyeur-house.tv/${REALM}/${CAM} - ${TIMESTAMP} - %(id)s.%(ext)s"
    my_thread = Process(target=dlv.main, args=(
        ['--cookie', cookie, '--template', template, PLAYLIST_URL],))
    my_thread.start()
    time.sleep(10.0)  # ONE_HOUR
    if my_thread.is_alive():
        print('killing dlv')
        my_thread.terminate()


if __name__ == "__main__":
    download()
