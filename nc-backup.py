import os
import subprocess
import sys
import argparse
import json

from urllib.request import urlretrieve
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoAlertPresentException

from tqdm import tqdm
from pathvalidate import sanitize_filename

def do_backup(args):

    cafe_url = "https://cafe.naver.com/" + args.cafe_name + "/"
    try:
        options = Options()
        options.add_argument('--disable-proxy-certificate-handler')
        options.add_argument('--ignore-certificate-errors-spki-list')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=options
        )
        driver.get("https://nid.naver.com/nidlogin.login?mode=form&url=https://www.naver.com/")
        driver.implicitly_wait(1)
        input('네이버에 로그인한 후 엔터 키를 누르세요...\nPress Enter after logging in to Naver...')
    except:
        print('오류: Chrome Web Driver 초기화에 실패했습니다. Chrome이 설치되지 않았거나, 지원되지 않는 버전의 Chrome입니다.')
        print('Error: Chrome Web Driver initialization failed. Chrome is not installed, or your version of Chrome is not supported.')
        sys.exit(1)


    if os.path.exists(args.wk_path) != True:
        print('오류: 이 프로그램은 Windows용 wkHTMLtoPDF를 필요로 합니다. wkHTMLtoPDF를 설치하거나 정확한 경로를 입력하고 다시 실행하세요.')
        print('Error: This program requires wkHTMLtoPDF for Windows. Please install wkHTMLtoPDF or enter the correct path and restart the program.')
        sys.exit(1)


    article_list = []
    if args.mode == 'single': # Backup a single article
        article_list = list(range(args.article_id, args.article_id + 1))

    elif args.mode == 'range': # Backup a range of articles
        article_list = list(range(args.article_start, args.article_end + 1))

    elif args.mode == 'my-articles': # Backup all articles written by you
        driver.get(cafe_url)
        driver.implicitly_wait(1)
        driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, '//button[text()="나의활동"]'))
        link = driver.find_element(By.XPATH, '//*[@id="ia-action-data"]/div[2]/ul/li[3]/span/strong/a').get_attribute('href')
        
        page = 1
        while True:
            driver.get(link + '&page=' + str(page))
            driver.implicitly_wait(1)
            articles = driver.find_elements(By.CLASS_NAME, 'inner_number')
            if len(articles) == 0:
                break
            for args.article in articles:
                article_list.append(int(args.article.text.strip()))
            page += 1


    i = 1
    l = len(article_list)
    success_count = 0
    image_ext = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg', 'tiff', 'tif', 'jfif', 'jp2', 'j2k', 'jpf', 'jpx', 'jpm', 'mj2']

    for article_id in tqdm(article_list):
        article_url = cafe_url + str(article_id)
        driver.get(article_url)
        driver.switch_to.frame('cafe_main')
        article_title = sanitize_filename(driver.find_element(By.XPATH, "//h3[@class='title_text']").text.strip())
        driver.implicitly_wait(2)

        try:
            alert = driver.switch_to.alert
            alert.accept()
            print("Error: Skipping article id %d. Article does not exist or inaccessible." % (i, l, article_id))
        except NoAlertPresentException:
            save_dir = "%s/%s/%d_%s" % (args.root_dir, args.cafe_name, article_id, article_title)
            if not os.path.isdir(save_dir):
                os.makedirs(save_dir)

            print("\nCrawling article id %d [%s]..." % (article_id, article_title))

            if args.download_img == True: # download images
                img_dir = "%s/img/" % save_dir

                imgs = driver.find_elements(By.XPATH, "//img[@class='article_img ATTACH_IMAGE' or @class='img' or @class='se-image-resource']")
                if len(imgs) > 0:
                    if not os.path.isdir(img_dir):
                        os.mkdir(img_dir)

                    for idx, img in enumerate(imgs):
                        img_url = img.get_attribute('src')
                        ext = 'png'
                        for e in image_ext:
                            if e in img_url.split('.')[-1]:
                                ext = e
                                break
                        print("Downloading image [%d / %d]..." % (idx+1, len(imgs)))
                        try:
                            urlretrieve(img_url, '%s/%s_%d.%s' % (img_dir, article_title, idx, ext))
                        except:
                            continue
            

            if args.download_vid == True: # download videos
                vid_dir = "%s/vid/" % save_dir

                def download_video(vids):
                    if len(vids) > 0:
                        if not os.path.isdir(vid_dir):
                            os.mkdir(vid_dir)
                        for idx, vid_url in enumerate(vids):
                            print("Downloading video [%d / %d]..." % (idx+1, len(vids)))
                            try:
                                urlretrieve(vid_url, '%s/%s_%d.mp4' % (vid_dir, article_title, idx))
                            except:
                                continue

                btn_list = driver.find_elements(By.XPATH, "//button[@class='pzp-button pzp-pc-playback-switch pzp-pc__playback-switch pzp-pc-ui-button']")
                if len(btn_list) == 0:
                    vids = []
                    iframe_list = driver.find_elements(By.TAG_NAME, 'iframe')
                    if len(iframe_list) > 0:
                        for iframe in iframe_list:
                            try:
                                if '//serviceapi.nmv.naver.com/' in iframe.get_attribute('src'):
                                    driver.get(iframe.get_attribute('src'))
                                    driver.implicitly_wait(1)
                                    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, "//div[@class='u_rmc_btn play_anim u_rmc_btn_play']"))
                                    vids.append(driver.find_element(By.TAG_NAME, 'video'))
                            except:
                                continue

                        vid_urls = [vid.get_attribute('src') for vid in vids]
                        download_video(vid_urls)

                        driver.get(article_url)
                        driver.switch_to.frame('cafe_main')
                        driver.implicitly_wait(1)
                
                else:
                    for btn in btn_list:
                        driver.execute_script("arguments[0].click();", btn)
                        driver.implicitly_wait(1)

                    vids = driver.find_elements(By.CLASS_NAME, 'webplayer-internal-video')
                    if vids[0].get_attribute('src')[:5] == 'blob:': # blob video
                        print("Blob video detected. Extracting video URLs...")
                        logs_raw = driver.get_log("performance")
                        logs = [json.loads(lr["message"])["message"] for lr in logs_raw]

                        def log_filter(log_):
                            return (
                                # is an actual response
                                log_["method"] == "Network.responseReceived"
                                # and json
                                and "json" in log_["params"]["response"]["mimeType"]
                            )
                        
                        vid_urls = []
                        for log in filter(log_filter, logs):
                            request_id = log["params"]["requestId"]
                            resp_url = log["params"]["response"]["url"]
                            if '/vod/play' in resp_url:
                                body = (driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id}))['body']
                                body = json.loads(body)
                                vid_list = body['videos']['list']
                                selected_vid = vid_list[0]
                                for vid in vid_list[1:]:
                                    if vid['size'] > selected_vid['size']:
                                        selected_vid = vid
                                vid_urls.append(selected_vid['source'])

                    else:
                        vid_urls = [vid.get_attribute('src') for vid in vids]

                    download_video(vid_urls)


            if args.download_attach == True: # download attachments
                attach_dir = "%s/attachments/" % save_dir
                
                attachments = driver.find_elements(By.CLASS_NAME, 'AttachFileListItem')
                urls = driver.find_elements(By.XPATH, '//div[@class="file_download"]/a[1]')
                if len(attachments) > 0:
                    if not os.path.isdir(attach_dir):
                        os.mkdir(attach_dir)

                    for idx, attach in enumerate(attachments):
                        filename = attach.find_element(By.CLASS_NAME, 'text').get_attribute("innerHTML").strip()
                        attach_url = urls[idx].get_attribute('href')
                        print("Downloading attachment [%d / %d]..." % (idx+1, len(attachments)))
                        try:
                            urlretrieve(attach_url, '%s/%s' % (attach_dir, filename))
                        except:
                            continue


            # download pdf
            html = driver.page_source.encode('utf-8')
            html = html.decode('utf-8')

            f = open('%s/%d_%s.html' % (save_dir, article_id, article_title), 'w', encoding='UTF-8')
            html = html.replace(u'<iframe title="답변쓰기에디터"', u'w')
            html = html.replace(u'<iframe src="//serviceapi.nmv.naver.com/', u'w')
            html = html.replace('<meta name=\"robots\" content=\"noindex, nofollow\">' , '<meta charset=\"UTF-8\">' , 1)
            f.write(html)
            f.close()

            subprocess.call('"%s" --encoding UTF-8 "%s/%d_%s.html" "%s/%d_%s.pdf"'
                            % (args.wk_path, save_dir, article_id, article_title, save_dir, article_id, article_title), shell=False)
            
            print("Successfully archived article id %d" % article_id)
            success_count += 1

    print('Successfully backed up %d out of %d articles.' % (success_count, l))


if __name__ == "__main__":
    username = os.environ.get('USERNAME')

    parser = argparse.ArgumentParser(prog="nc-backup",
                                     description="Naver Cafe Article Backup Tool",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    subparsers = parser.add_subparsers(help='sub-command help', dest='mode', required=True)
    parser_single = subparsers.add_parser("single", help="Backup a single article",
                                       formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_range = subparsers.add_parser("range", help="Backup a range of articles",
                                       formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_my = subparsers.add_parser("my-articles", help="Backup all articles written by you",
                                       formatter_class=argparse.ArgumentDefaultsHelpFormatter)


    parser.add_argument('--cafe-name', type=str, help='Naver cafe name, the one at the end of the url (https://cafe.naver.com/[name]/)', required=True)
    parser.add_argument('--root-dir', type=str, help='Root directory for storing backups', default='C:/Users/%s/Documents/NaverCafeBackups' % username)
    parser.add_argument('--wk-path', type=str, help='Path to wkHTMLtoPDF', default='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
    parser.add_argument('--download-img', type=bool, help='Download images', default=True)
    parser.add_argument('--download-vid', type=bool, help='Download videos', default=True)
    parser.add_argument('--download-attach', type=bool, help='Download attachments', default=True)

    parser_single.add_argument('--article-id', type=int, help='ID of the article to backup (https://cafe.naver.com/[name]/[id])', required=True)

    parser_range.add_argument('--article-start', type=int, help='Start ID of the range of articles to backup (https://cafe.naver.com/[name]/[id])', default=1)
    parser_range.add_argument('--article-end', type=int, help='End ID of the range of articles to backup (https://cafe.naver.com/[name]/[id])', required=True)

    args = parser.parse_args()
    do_backup(args)