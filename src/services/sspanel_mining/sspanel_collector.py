import time
import random
import sys
from typing import Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from tqdm import tqdm

from services.utils.toolbox.toolbox import get_ctx
from services.sspanel_mining.exceptions import CollectorSwitchError
from services.utils.proxy_manager import ProxyManager

class SSPanelHostsCollector:
    def __init__(
            self,
            path_file_txt: str,
            silence: bool = True,
            debug: bool = False,
    ):
        """

        :param path_file_txt:
        :param silence:
        :param debug:
        """
        # 筛选 Malio 站点
        self._QUERY = "由 @editXY 修改适配。"

        # 全量搜集
        # self._QUERY = 'inurl:staff "SSPanel V3 Mod UIM"'

        # 随机选择不同的搜索查询，减少被检测的可能性
        search_queries = [
            "由 @editXY 修改适配。",
            'inurl:staff "SSPanel V3 Mod UIM"',
            "SSPanel V3 Mod UIM",
            "SSPanel UIM",
            "SSPanel 面板"
        ]
        self._QUERY = random.choice(search_queries)

        self.GOOGLE_SEARCH_API = f'https://www.google.com.hk/search?q="{self._QUERY}"&filter=0'
        self.path_file_txt = path_file_txt
        self.debug = debug
        self.silence = silence
        self.page_num = 1
        
        # 初始化代理管理器
        self.proxy_manager = ProxyManager()
        self.current_proxy = None

    @staticmethod
    def _down_to_api(api, search_query: str):
        """检索关键词并跳转至相关页面"""
        while True:
            try:
                input_tag = api.find_element(By.XPATH, "//input[@name='q']")
                try:
                    input_tag.click()
                # 无头模式运行会引发错误
                except ElementClickInterceptedException:
                    pass
                input_tag.clear()
                input_tag.send_keys(search_query)
                input_tag.send_keys(Keys.ENTER)
                break

            except NoSuchElementException:
                time.sleep(0.5)
                continue

    @staticmethod
    def _page_switcher(api, is_home_page: bool = False):
        start_time = time.time()
        # 首页 -> 第二页
        if is_home_page:
            while True:
                try:
                    # 随机滚动行为
                    scroll_actions = [
                        lambda: ActionChains(api).send_keys(Keys.PAGE_DOWN).perform(),
                        lambda: ActionChains(api).send_keys(Keys.END).perform(),
                    ]
                    random.choice(scroll_actions)()
                    
                    time.sleep(random.uniform(0.5, 1.0))
                    api.find_element(By.XPATH, "//a[@id='pnnext']").click()
                    break
                except NoSuchElementException:
                    # 检测到到流量拦截 主动抛出异常并采取备用方案
                    if "sorry" in api.current_url:
                        raise CollectorSwitchError
                    time.sleep(random.uniform(0.5, 1.0))
                    api.refresh()
                    continue
        # 第二页 -> 第N页
        else:
            while True:
                try:
                    # 随机滚动行为
                    scroll_actions = [
                        lambda: ActionChains(api).send_keys(Keys.PAGE_DOWN).perform(),
                        lambda: ActionChains(api).send_keys(Keys.END).perform(),
                    ]
                    random.choice(scroll_actions)()
                    
                    time.sleep(random.uniform(0.5, 1.0))
                    page_switchers = api.find_elements(By.XPATH, "//a[@id='pnnext']")
                    next_page_bottom = page_switchers[-1]
                    next_page_bottom.click()
                    break
                except (NoSuchElementException, IndexError):
                    time.sleep(random.uniform(0.5, 1.0))
                    # 检测到到流量拦截 主动抛出异常并采取备用方案
                    if "sorry" in api.current_url:
                        raise CollectorSwitchError
                    # 最后一页
                    if time.time() - start_time > 5:
                        break
                    continue

    def _page_tracking(self, api, ignore_filter=True):
        next_obj = None
        start_time = time.time()
        
        # 添加随机延迟，模拟人类行为
        time.sleep(random.uniform(1, 3))
        
        while True:
            try:
                # 随机滚动页面，模拟人类浏览行为
                scroll_actions = [
                    lambda: ActionChains(api).send_keys(Keys.PAGE_DOWN).perform(),
                    lambda: ActionChains(api).send_keys(Keys.END).perform(),
                    lambda: ActionChains(api).send_keys(Keys.PAGE_UP).perform(),
                ]
                random.choice(scroll_actions)()
                
                time.sleep(random.uniform(0.5, 1.5))
                next_obj = api.find_element(By.XPATH, "//a[@id='pnnext']")
                break
            except NoSuchElementException:
                time.sleep(random.uniform(0.5, 1.0))
                # 检测到到流量拦截 主动抛出异常并采取备用方案
                if "sorry" in api.current_url:
                    # windows调试环境中，手动解决 CAPTCHA
                    if 'win' in sys.platform and not self.silence:
                        input("\n--> 遭遇拦截，本开源代码未提供相应解决方案。\n"
                              "--> 请开发者手动处理 reCAPTCHA 并于控制台输入任意键继续执行程序\n"
                              f">>>")
                        continue
                    raise CollectorSwitchError
                # 最后一页
                if time.time() - start_time > 5:
                    break
                continue

        if next_obj:
            next_url = next_obj.get_attribute("href")
            if ignore_filter:
                next_url = next_url + "&filter=0"
            
            # 添加随机延迟，模拟人类点击行为
            time.sleep(random.uniform(1, 2))
            api.get(next_url)
            return True
        else:
            return False

    def _capture_host(self, api):
        # 随机延迟，模拟人类阅读时间
        time.sleep(random.uniform(2, 5))
        
        # 随机滚动页面
        scroll_actions = [
            lambda: ActionChains(api).send_keys(Keys.PAGE_DOWN).perform(),
            lambda: ActionChains(api).send_keys(Keys.END).perform(),
            lambda: ActionChains(api).send_keys(Keys.PAGE_UP).perform(),
            lambda: ActionChains(api).send_keys(Keys.HOME).perform(),
        ]
        random.choice(scroll_actions)()
        
        # 再次随机延迟
        time.sleep(random.uniform(1, 3))
        
        hosts = api.find_elements(
            By.XPATH,
            "//div[contains(@class,'NJjxre')]//cite[@class='iUh30 qLRx3b tjvcx']"
        )

        with open(self.path_file_txt, "a", encoding="utf8") as f:
            for host in hosts:
                f.write(f"{host.text.split(' ')[0].strip()}/auth/register\n")

    def reset_page_num(self, api):
        try:
            result = api.find_element(By.XPATH, "//div[@id='result-stats']")
            tag_num = result.text.strip().split(" ")[1]
            self.page_num = int(int(tag_num) / 10) + 1 if tag_num else 26
            return self.page_num
        except NoSuchElementException:
            return None

    @staticmethod
    def set_loop_progress(total: int):
        return tqdm(
            total=total,
            desc="SSPanel COLLECTOR",
            ncols=150,
            unit="piece",
            dynamic_ncols=False,
            leave=True,
        )

    def reset_loop_progress(self, api, new_status: str = None):
        page_num_result = self.reset_page_num(api=api)
        if page_num_result is not None:
            self.page_num = page_num_result
        loop_progress = self.set_loop_progress(self.page_num)
        if new_status is not None:
            loop_progress.set_postfix({"status": new_status})

    def run(self, page_num: int = None, sleep_node: int = 5):
        """

        :param page_num: 期望采集数量
        :param sleep_node: 休眠间隔
        :return:
        """
        self.page_num = 26 if page_num is None else page_num

        loop_progress = self.set_loop_progress(self.page_num)
        loop_progress.set_postfix({"status": "__initialize__"})

        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # 获取新代理
                if self.current_proxy:
                    self.proxy_manager.mark_proxy_failed(self.current_proxy)
                
                self.current_proxy = self.proxy_manager.get_proxy()
                if self.current_proxy:
                    self.proxy_manager.set_proxy_environment(self.current_proxy)
                    print(f"使用代理: {self.current_proxy}")
                else:
                    print("警告: 没有可用代理，将使用直连")
                
                with get_ctx(silence=self.silence) as ctx:
                    ctx.get(self.GOOGLE_SEARCH_API)
                    self.reset_loop_progress(api=ctx, new_status="__pending__")

                    # 获取page_num页的注册链接
                    # 正常情况一页10个链接 既共获取page_num * 10个链接
                    ack_num = 0
                    while True:
                        ack_num += 1
                        """
                        [🛴]采集器
                        ___________
                        萃取注册链接并保存
                        """
                        self._capture_host(api=ctx)
                        loop_progress.update(1)
                        loop_progress.set_postfix({"status": "__collect__"})

                        """
                        [🛴]翻页控制器
                        ___________
                        页面追踪
                        """
                        try:
                            res = self._page_tracking(api=ctx)
                            if ack_num >= self.page_num:
                                self.reset_loop_progress(api=ctx, new_status="__reset__")
                                loop_progress.update(ack_num)
                            if not res:
                                # 标记代理成功
                                if self.current_proxy:
                                    self.proxy_manager.mark_proxy_success(self.current_proxy)
                                return
                        except CollectorSwitchError:
                            # 重新抛出异常，让外层重试机制处理
                            raise

                        """
                        [🛴]休眠控制器
                        ___________
                        每sleep_node页进行一次随机时长的休眠
                        """
                        if ack_num % sleep_node == 0:
                            tax_ = random.uniform(3, 5)
                            loop_progress.set_postfix({"status": "__sleep__"})
                            time.sleep(tax_)
                            
                # 如果成功完成，标记代理成功并跳出重试循环
                if self.current_proxy:
                    self.proxy_manager.mark_proxy_success(self.current_proxy)
                break
                
            except CollectorSwitchError as e:
                retry_count += 1
                if retry_count < max_retries:
                    print(f"\n[WARNING] 检测到Google拦截，正在进行第{retry_count}次重试...")
                    print(f"[INFO] 等待{retry_count * 30}秒后重试...")
                    time.sleep(retry_count * 30)  # 递增等待时间
                    
                    # 重置进度条
                    loop_progress = self.set_loop_progress(self.page_num)
                    loop_progress.set_postfix({"status": f"__retry_{retry_count}__"})
                else:
                    print(f"\n[ERROR] 经过{max_retries}次重试后仍然被Google拦截")
                    print("[INFO] 建议：")
                    print("1. 检查网络连接")
                    print("2. 等待一段时间后重试")
                    print("3. 考虑使用代理或VPN")
                    print("4. 在Windows环境下可以手动处理验证码")
                    print("5. 运行代理搜集器获取更多代理")
                    raise e
