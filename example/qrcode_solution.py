import time
import datetime
import pprint
import json
import os
import requests
from playwright.sync_api import sync_playwright
from xhs import DataFetchError, XhsClient, help, SignError
from .sign import sign
from .xhs_predict import predict_rotation_angle

import requests
import logging
import logging.handlers
import sys
log_handlers = [
    logging.handlers.RotatingFileHandler(
        filename="core.log", maxBytes=1024 * 1024 * 1024, backupCount=5
    ),
    logging.StreamHandler(sys.stdout),
]
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - [File: %(pathname)s, Line: %(lineno)d] - %(name)s - %(levelname)s %(threadName)s - %(message)s",
    handlers=log_handlers,
)

logger = logging.getLogger(__name__)


def handle_captcha(verify_uuid: str):
    logger.info("开始处理验证码")
    verifyType = 102
    verifyBiz = 461
    with sync_playwright() as playwright:
        stealth_js_path = "/Users/lisaifei/code/js/stealth.min.js/stealth.min.js"
        chromium = playwright.chromium
        # 如果一直失败可尝试设置成 False 让其打开浏览器，适当添加 sleep 可查看浏览器状态
        browser = chromium.launch(headless=True)

        browser_context = browser.new_context()
        browser_context.add_init_script(path=stealth_js_path)
        context_page = browser_context.new_page()
        captcha_base_url = f"https://www.xiaohongshu.com/website-login/captcha?verifyUuid={verify_uuid}&verifyType={verifyType}&verifyBiz={verifyBiz}"

        context_page.goto(f"{captcha_base_url}")
        captcha_rotate_elm_id = "red-captcha-rotate"
        captcha_rotate_bg_elm_id = "red-captcha-rotate-bg"
        rotate_img_elm = context_page.wait_for_selector(f"#{captcha_rotate_elm_id} img")
        rotate_bg_img_elm = context_page.wait_for_selector(f"#{captcha_rotate_bg_elm_id} img")
        logger.info(f"获取验证码图片: {rotate_img_elm}")
        rotate_img_elm_src = rotate_img_elm.get_attribute("src")
        logger.info(f"获取验证码图片地址: {rotate_img_elm_src}")
        rotate_bg_img_elm_src = rotate_bg_img_elm.get_attribute("src")
        logger.info(f"获取验证码背景图片地址: {rotate_bg_img_elm_src}")
        cur_file_dir = os.path.dirname(os.path.abspath(__file__))
        image_dir = f"{cur_file_dir}/images"
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)
        # download image
        response = requests.get(rotate_img_elm_src)
        date_str = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        captcha_rotate_img_path = f"{image_dir}/captcha_rotate_img_{date_str}.jpg"
        with open(f"{captcha_rotate_img_path}", "wb") as f:
            f.write(response.content)
        captcha_rotate_bg_img_path = f"{image_dir}/captcha_rotate_bg_img_{date_str}.jpg"
        response = requests.get(rotate_bg_img_elm_src)
        with open(f"{captcha_rotate_bg_img_path}", "wb") as f:
            f.write(response.content)
        # 获取旋转角度
        predict_angle = predict_rotation_angle(captcha_rotate_img_path)
        logger.info(f"预测旋转角度: {predict_angle}")


if __name__ == '__main__':
    # cookie = "please get cookie from your website"
    # 创作者平台 cookie
    # cookie = "abRequestId=6a42c3f7-5f4c-572e-9847-bc733cc61073; a1=18f74e3b0e2m6jaraiqcaajn8bmz3765wou17xhp030000156562; webId=6cf889e2d027fb9172e3e69efc3394dc; gid=yYiW4dqDYiEJyYiW4dqD8lCxdJ6KV0F03AS07U80VIYD6yq8uqWK2W888y2K2KJ8K8JJKiYi; webBuild=4.23.1; web_session=040069799389ab765b50c77948344b6fee1224; unread={%22ub%22:%2266826a22000000000a006b1b%22%2C%22ue%22:%22668286a8000000001c0252fc%22%2C%22uc%22:23}; galaxy_creator_session_id=OT0dYdzr4xp4BbXOHPSw7wU5q0ykHVgHjYgN; galaxy.creator.beaker.session.id=1719899156825057015083; websectiga=cf46039d1971c7b9a650d87269f31ac8fe3bf71d61ebf9d9a0a87efb414b816c; sec_poison_id=479e8d7d-a67d-43fb-a261-cc7c434eda8f; acw_tc=3915dbe92c75328125cf3ff52afa8e4766baa348ccce76d666fec9d9fbea9fab; xsecappid=ugc"

    # 小红书主站cookie
    # cookie = "abRequestId=6a42c3f7-5f4c-572e-9847-bc733cc61073; a1=18f74e3b0e2m6jaraiqcaajn8bmz3765wou17xhp030000156562; webId=6cf889e2d027fb9172e3e69efc3394dc; gid=yYiW4dqDYiEJyYiW4dqD8lCxdJ6KV0F03AS07U80VIYD6yq8uqWK2W888y2K2KJ8K8JJKiYi; web_session=040069799389ab765b50c77948344b6fee1224; galaxy_creator_session_id=OT0dYdzr4xp4BbXOHPSw7wU5q0ykHVgHjYgN; galaxy.creator.beaker.session.id=1719899156825057015083; webBuild=4.24.2; xsecappid=xhs-pc-web; websectiga=cffd9dcea65962b05ab048ac76962acee933d26157113bb213105a116241fa6c; sec_poison_id=f8aaf8d3-fd76-4d67-b319-ad0a6bf4efa8; acw_tc=2a54bc6021d83f354d7d4742760e35d226dbfa3d8f2010167224c2bae646bb7e; unread={%22ub%22:%2266851447000000001c025596%22%2C%22ue%22:%22666585640000000006006a72%22%2C%22uc%22:30}"

    # cookie_dict = {
    #     'a1': '1900bea6f9e9h7czba2xxzg7pa0hwc8k9hz1i82ke30000346660',
    #     'abRequestId': '8a31b417-005e-5bb3-ae6d-cfdbf5fe2a22',
    #     'acw_tc': '3aa6b00271a9bdb13d82e01b25a3763ed6aabbb72e4c368900ac724334911e31',
    #     'gid': 'yj88Dd0W4ij2yj88Dd0KixYJjdjxWSuD0JCCuTdukWU08yq8xESYT3888q4KKK88Yq488DSq',
    #     'sec_poison_id': 'dc3ef299-6bcc-41e7-a2d4-850ffea0dcd8',
    #     'unread': '{%22ub%22:%226666cd8100000000150094cc%22%2C%22ue%22:%2266681db6000000001c0200d2%22%2C%22uc%22:15}',
    #     'webBuild': '4.20.1',
    #     'webId': '9bffa11af74ef2645f1b647088928efc',
    #     'web_session': '040069799389ab765b50c77948344b6fee1224',
    #     'websectiga': '7750c37de43b7be9de8ed9ff8ea0e576519e8cd2157322eb972ecb429a7735d4',
    #     'xsecappid': 'xhs-pc-web'
    # }
    # cookie = ";".join([f"{k}={v}" for k, v in cookie_dict.items()])
    # cookie = "a1=18fbe30ddab17ylyyonpkkb4gp1h04y0656vk2zte30000374819; webId=1604258d2ba30e619c1481f57cd5ee00;web_session=040069b732b257640588a95d62344b505767b8;"
    cookie = "web_session=040069b732b257640588a95d62344b505767b8;"

    xhs_client = XhsClient(cookie, sign=sign)

    search_count = 0
    for _ in range(10):
        # 即便上面做了重试，还是有可能会遇到签名失败的情况，重试即可
        try:
            note_id = '6603aa330000000014005158'
            comment_id = '660f9a6f000000001503883c'

            # 获取笔记详情
            # note = xhs_client.get_note_by_id(note_id)
            # pprint.pprint(note)

            # print(json.dumps(note, indent=4))
            # 获取笔记图片
            # print(help.get_imgs_url_from_note(note))

            verify_uuid = "276c3d06-2c55-4d5e-a96b-0a518e0f0d76*qYgPPlAG"
            handle_captcha(verify_uuid)
            break

        except DataFetchError as e:
            print(f"搜索次数: {search_count}")
            print(e)
            print("失败重试一下下")
