import os
import re
import requests
import time
import concurrent.futures
import subprocess
from datetime import datetime, timezone, timedelta

# ===============================
# 配置区
FOFA_URLS = {
    "https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjb3VudHJ5PSJDTiI%3D": "ip.txt",
}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

COUNTER_FILE = "计数.txt"
IP_DIR = "ip"
RTP_DIR = "rtp"
ZUBO_FILE = "zubo.txt"
IPTV_FILE = "IPTV.txt"

# ===============================
# 分类与映射配置
CHANNEL_CATEGORIES = {
"央视频道":[
"CCTV-1综合","CCTV-2财经","CCTV-3综艺","CCTV-4中文国际","CCTV-5体育","CCTV-5+体育赛事","CCTV-6电影","CCTV-7国防军事","CCTV-8电视剧","CCTV-9纪录","CCTV-10科教","CCTV-11戏曲","CCTV-12社会与法","CCTV-13新闻","CCTV-14少儿","CCTV-15音乐","CCTV-16奥林匹克","CCTV-16奥林匹克4K","CCTV-17农业农村","CCTV-4欧洲","CCTV-4美洲","CCTV-4K","CCTV-8K","中央新影-中学生","中央新影-老故事","中央新影-发现之旅","CGTN","CGTN-纪录","CGTN-法语","CGTN-俄语","CGTN-西班牙语","CGTN-阿拉伯语","中国教育1台","中国教育2台","中国教育4台","早期教育"
],
"付费频道":[
"风云剧场","怀旧剧场","第一剧场","风云足球","央视台球","高尔夫·网球","风云音乐","央视文化精品","卫生健康","电视指南","兵器科技","女性时尚","世界地理","CHC家庭影院","CHC动作电影","CHC影迷电影"
],
"卫视频道":[
"山东卫视", "湖南卫视", "浙江卫视", "江苏卫视", "东方卫视", "深圳卫视", "北京卫视", "广东卫视", "广西卫视", "东南卫视", "海南卫视","河北卫视", "河南卫视", "湖北卫视", "江西卫视", "四川卫视", "重庆卫视", "贵州卫视", "云南卫视", "天津卫视", "安徽卫视","辽宁卫视", "黑龙江卫视", "吉林卫视", "内蒙古卫视", "宁夏卫视", "山西卫视", "陕西卫视", "甘肃卫视", "青海卫视","新疆卫视", "西藏卫视", "三沙卫视", "兵团卫视", "延边卫视", "安多卫视", "康巴卫视", "农林卫视", "山东教育卫视","大湾区卫视","海峡卫视","西藏卫视藏语","安多卫视藏语","康巴卫视藏语","内蒙古卫视蒙语"
],
"高清频道":[
"北京卫视4K","广东卫视4K","深圳卫视4K","山东卫视4K","湖南卫视4K","浙江卫视4K","江苏卫视4K","东方卫视4K","四川卫视4K"
],
"数字频道":[
"金鹰纪实", "金鹰卡通", "快乐垂钓", "茶频道", "求索纪录", "中国天气", "天元围棋", "睛彩竞技", "睛彩篮球", "睛彩青少年", "睛彩广场舞","北京纪实科教","金鹰纪实","金鹰卡通","重温经典电影","少儿动画","卡酷少儿","动漫秀场","嘉佳卡通","优漫卡通","哈哈炫动","新动漫","优优宝贝","金色学堂","求索纪录","乐游","游戏风云","都市剧场","法治天地","梨园频道","武术世界","茶频道","文物宝库","精彩影视","生活时尚","中国交通","汽摩频道","魅力足球","先锋乒羽","快乐垂钓","四海钓鱼","中华特产","环球旅游","东方财经","书画频道","生态环境","家庭理财","财富天下","车迷频道","海洋频道"
],
"山东频道":[
"山东齐鲁","山东体育","山东农科","山东新闻","山东少儿","山东文旅","山东综艺","山东生活","山东教育卫视","山东居家购物","QTV-1","QTV-2","QTV-3","QTV-4","QTV-5","崂山综合","黄岛综合","黄岛生活","胶州综合","平度新闻","莱西综合","济南新闻","济南新闻","济南教育","济南都市","济南生活","济南文旅教育","济南娱乐","济南少儿","济南鲁中","历城综合","长清新闻","济阳综合","平阴综合","商河综合","淄博新闻","淄博影视","淄博文旅","淄博民生","张店综合","淄川新闻","周村新闻","桓台综合","高青综合","沂源新闻","东营综合","东营公共","广饶新闻","烟台新闻","烟台公共","烟台经济科教","烟台影视","牟平新闻","牟平生活","蓬莱新闻","龙口综合","招远综合","栖霞综合","海阳综合","海阳综艺","长岛综合","潍坊新闻","潍坊经济生活","潍坊影视综艺","潍坊科教文旅","潍坊高新区","青州新闻","青州文旅","诸城新闻","寿光新闻","寿光蔬菜","安丘新闻","高密综合","昌邑综合","昌乐综合","临朐综合","济宁综合","济宁生活","济宁公共","济宁高新","任城-1","任城-2","兖州新闻","曲阜新闻综合","邹城综合","鱼台新闻","鱼台生活","嘉祥综合","梁山综合","泰山电视","肥城综合","岱岳有线","新泰综合","新泰乡村","宁阳综合","宁阳影视","东平新闻","威海新闻","威海都市生活","文登综合","荣成综合","乳山综合","日照新闻","日照科教","日照公共","莒县综合","岚山综合","河东综合","沂水综合","沂水生活","兰陵综合","兰陵公共","五莲新闻","蒙阴综合","临沭综合","莒南综合","德州新闻综合","德州经济生活","陵城新闻","禹城综合","禹城综艺","宁津综合","齐河综合","武城新闻","武城综艺影视","平原新闻","夏津新闻","夏津公共","临邑综合","聊城综合","聊城民生","茌平新闻","临清综合","莘县综合","冠县综合","东阿综合","滨州综合","滨州民生","沾化综合","邹平新闻","惠民综合","阳信新闻","无棣新闻","菏泽新闻","菏泽生活","定陶TV-1","单县综合","鄄城新闻","郓城综合","巨野新闻","东明新闻","汶上综合","山东经济广播","山东交通广播"
],
"广东频道":[
"广东体育","广东珠江","广东影视","广东民生","广东现代教育","广东经济科教","广东新闻","岭南戏曲","广东嘉佳卡通","广东少儿","广东综艺4K","广州综合","广州新闻","广州影视","广州法治","南国都市4K","深圳都市","深圳电视剧","深圳龙岗","深圳财经生活","深圳体育健康","深圳少儿","深圳众创TV","宝安频道","佛山综合","佛山影视","佛山公共","东莞综合","东莞资讯","佛山顺德","佛山南海","珠海综合","汕尾综合","汕尾文化生活","韶关综合","湛江综合","湛江公共","江门综合","江门侨乡生活","茂名综合","茂名文化生活","揭阳综合","揭阳生活","云浮综合","云浮文旅","汕头综合","汕头经济生活","汕头经济","汕头文旅体育","汕头体育","惠州-1","惠州-2","潮州综合","潮州民生","梅州综合","梅州客家生活","中山综合","中山文化","阳江-1","阳江-2","肇庆综合","肇庆生活","清远综合","清远生活","河源综合","河源公共"
]
#任意添加，与仓库中rtp/省份运营商.txt内频道一致即可，或在下方频道名映射中改名
}
# ===== 映射（别名 -> 标准名） =====
CHANNEL_MAPPING = {

}#格式为"频道分类中的标准名": ["rtp/中的名字"],

# ===============================
# 计数逻辑
def get_run_count():
    if os.path.exists(COUNTER_FILE):
        try:
            return int(open(COUNTER_FILE).read().strip())
        except:
            return 0
    return 0

def save_run_count(count):
    open(COUNTER_FILE, "w").write(str(count))

def check_and_clear_files_by_run_count():
    os.makedirs(IP_DIR, exist_ok=True)
    count = get_run_count() + 1
    if count >= 73:
        print(f"🧹 第 {count} 次运行，清空 {IP_DIR} 下所有 .txt 文件")
        for f in os.listdir(IP_DIR):
            if f.endswith(".txt"):
                os.remove(os.path.join(IP_DIR, f))
        save_run_count(1)
        return "w", 1
    else:
        save_run_count(count)
        return "a", count

# ===============================
# IP 运营商判断
def get_isp(ip):
    if re.match(r"^(1[0-9]{2}|2[0-3]{2}|42|43|58|59|60|61|110|111|112|113|114|115|116|117|118|119|120|121|122|123|124|125|126|127|175|180|182|183|184|185|186|187|188|189|223)\.", ip):
        return "电信"
    elif re.match(r"^(42|43|58|59|60|61|110|111|112|113|114|115|116|117|118|119|120|121|122|123|124|125|126|127|175|180|182|183|184|185|186|187|188|189|223)\.", ip):
        return "联通"
    elif re.match(r"^(223|36|37|38|39|100|101|102|103|104|105|106|107|108|109|134|135|136|137|138|139|150|151|152|157|158|159|170|178|182|183|184|187|188|189)\.", ip):
        return "移动"
    else:
        return "未知"

# ===============================
# 第一阶段
def first_stage():
    all_ips = set()
    for url, filename in FOFA_URLS.items():
        print(f"📡 正在爬取 {filename} ...")
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            urls_all = re.findall(r'<a href="http://(.*?)"', r.text)
            all_ips.update(u.strip() for u in urls_all)
        except Exception as e:
            print(f"❌ 爬取失败：{e}")
        time.sleep(3)

    province_isp_dict = {}
    for ip_port in all_ips:
        try:
            ip = ip_port.split(":")[0]
            res = requests.get(f"http://ip-api.com/json/{ip}?lang=zh-CN", timeout=10)
            data = res.json()
            province = data.get("regionName", "未知")
            isp = get_isp(ip)
            if isp == "未知":
                continue
            fname = f"{province}{isp}.txt"
            province_isp_dict.setdefault(fname, set()).add(ip_port)
        except Exception:
            continue

    mode, run_count = check_and_clear_files_by_run_count()
    for filename, ip_set in province_isp_dict.items():
        path = os.path.join(IP_DIR, filename)
        with open(path, mode, encoding="utf-8") as f:
            for ip_port in sorted(ip_set):
                f.write(ip_port + "\n")
        print(f"{path} 已{'覆盖' if mode=='w' else '追加'}写入 {len(ip_set)} 个 IP")
    print(f"✅ 第一阶段完成，当前轮次：{run_count}")
    return run_count

# ===============================
# 第二阶段 - 修改为同时生成 rtp 和 udp 格式
def second_stage():
    print("🔔 第二阶段触发：生成 zubo.txt（支持 rtp 和 udp 格式）")
    combined_lines = []
    for ip_file in os.listdir(IP_DIR):
        if not ip_file.endswith(".txt"):
            continue
        ip_path = os.path.join(IP_DIR, ip_file)
        rtp_path = os.path.join(RTP_DIR, ip_file)
        if not os.path.exists(rtp_path):
            continue

        with open(ip_path, encoding="utf-8") as f1, open(rtp_path, encoding="utf-8") as f2:
            ip_lines = [x.strip() for x in f1 if x.strip()]
            rtp_lines = [x.strip() for x in f2 if x.strip()]

        if not ip_lines or not rtp_lines:
            continue

        for ip_port in ip_lines:
            for rtp_line in rtp_lines:
                if "," not in rtp_line:
                    continue
                ch_name, rtp_url = rtp_line.split(",", 1)
                
                # 提取组播地址
                multicast_match = re.search(r'rtp://(.+)', rtp_url)
                if multicast_match:
                    multicast_addr = multicast_match.group(1)
                    
                    # 生成 rtp 格式地址
                    rtp_format_url = f"http://{ip_port}/rtp/{multicast_addr}"
                    combined_lines.append(f"{ch_name},{rtp_format_url}")
                    
                    # 生成 udp 格式地址
                    udp_format_url = f"http://{ip_port}/udp/{multicast_addr}"
                    combined_lines.append(f"{ch_name},{udp_format_url}")

    # 去重
    unique = {}
    for line in combined_lines:
        url_part = line.split(",", 1)[1]
        if url_part not in unique:
            unique[url_part] = line

    with open(ZUBO_FILE, "w", encoding="utf-8") as f:
        for line in unique.values():
            f.write(line + "\n")
    print(f"🎯 第二阶段完成，共 {len(unique)} 条有效 URL（包含 rtp 和 udp 格式）")

# ===============================
# 第三阶段 - 修改为同时检测 rtp 和 udp 格式
def third_stage():
    print("🧩 第三阶段：多线程检测代表频道生成 IPTV.txt（支持 rtp 和 udp 格式）")

    if not os.path.exists(ZUBO_FILE):
        print("⚠️ zubo.txt 不存在，跳过")
        return

    def check_stream(url, timeout=5):
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_streams", "-i", url],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout + 2
            )
            return b"codec_type" in result.stdout
        except Exception:
            return False

    alias_map = {}
    for main_name, aliases in CHANNEL_MAPPING.items():
        for alias in aliases:
            alias_map[alias] = main_name

    ip_info = {}
    for fname in os.listdir(IP_DIR):
        if not fname.endswith(".txt"):
            continue
        province_operator = fname.replace(".txt", "")
        path = os.path.join(IP_DIR, fname)
        with open(path, encoding="utf-8") as f:
            for line in f:
                ip_port = line.strip()
                ip_info[ip_port] = province_operator

    groups = {}
    with open(ZUBO_FILE, encoding="utf-8") as f:
        for line in f:
            if "," not in line:
                continue
            ch_name, url = line.strip().split(",", 1)
            ch_main = alias_map.get(ch_name, ch_name)
            m = re.match(r"http://(\d+\.\d+\.\d+\.\d+:\d+)/", url)
            if m:
                ip_port = m.group(1)
                groups.setdefault(ip_port, []).append((ch_main, url))

    def detect_ip(ip_port, entries):
        # 检测 rtp 格式的代表频道
        rtp_rep_channels = [u for c, u in entries if c == "CCTV-1综合" and "/rtp/" in u]
        if not rtp_rep_channels:
            # 如果没有找到 CCTV-1综合，尝试其他代表频道
            rtp_rep_channels = [u for c, u in entries if c in ["CCTV-1综合", "CCTV1", "CCTV-1"] and "/rtp/" in u]
        
        # 检测 udp 格式的代表频道
        udp_rep_channels = [u for c, u in entries if c == "CCTV-1综合" and "/udp/" in u]
        if not udp_rep_channels:
            # 如果没有找到 CCTV-1综合，尝试其他代表频道
            udp_rep_channels = [u for c, u in entries if c in ["CCTV-1综合", "CCTV1", "CCTV-1"] and "/udp/" in u]
        
        # 如果都没有找到代表频道，使用第一个频道作为代表
        if not rtp_rep_channels and not udp_rep_channels and entries:
            first_channel = entries[0][1]
            if "/rtp/" in first_channel:
                rtp_rep_channels = [first_channel]
            else:
                udp_rep_channels = [first_channel]
        
        # 检测两种格式的代表频道
        rtp_playable = any(check_stream(u) for u in rtp_rep_channels) if rtp_rep_channels else False
        udp_playable = any(check_stream(u) for u in udp_rep_channels) if udp_rep_channels else False
        
        return ip_port, rtp_playable, udp_playable

    print(f"🚀 启动多线程检测（共 {len(groups)} 个 IP）...")
    playable_ips = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(detect_ip, ip, chs): ip for ip, chs in groups.items()}
        for future in concurrent.futures.as_completed(futures):
            ip_port, rtp_ok, udp_ok = future.result()
            playable_ips[ip_port] = {"rtp": rtp_ok, "udp": udp_ok}

    print(f"✅ 检测完成，可播放 IP 统计：")
    rtp_count = sum(1 for ip in playable_ips.values() if ip["rtp"])
    udp_count = sum(1 for ip in playable_ips.values() if ip["udp"])
    print(f"   - RTP 格式可用: {rtp_count} 个")
    print(f"   - UDP 格式可用: {udp_count} 个")
    print(f"   - 总计可用 IP: {len([ip for ip in playable_ips.values() if ip['rtp'] or ip['udp']])} 个")

    valid_lines = []
    seen = set()

    for ip_port, formats in playable_ips.items():
        province_operator = ip_info.get(ip_port, "未知")
        
        # 只处理可用的格式
        available_formats = []
        if formats["rtp"]:
            available_formats.append("rtp")
        if formats["udp"]:
            available_formats.append("udp")
            
        if not available_formats:
            continue
            
        # 获取该IP的所有频道
        for c, u in groups[ip_port]:
            # 检查URL格式是否可用
            url_format = "rtp" if "/rtp/" in u else "udp"
            if url_format in available_formats:
                key = f"{c},{u}"
                if key not in seen:
                    seen.add(key)
                    valid_lines.append(f"{c},{u}${province_operator}")

    beijing_now = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
    disclaimer_url = "https://kakaxi-1.asia/LOGO/Disclaimer.mp4"

    with open(IPTV_FILE, "w", encoding="utf-8") as f:
        f.write(f"#更新时间: {beijing_now}（北京时间）\n\n")
        f.write("#更新时间,#genre#\n")
        f.write(f"#{beijing_now},{disclaimer_url}\n\n")

        for category, ch_list in CHANNEL_CATEGORIES.items():
            f.write(f"{category},#genre#\n")
            for ch in ch_list:
                for line in valid_lines:
                    name = line.split(",", 1)[0]
                    if name == ch:
                        f.write(line + "\n")
            f.write("\n")

    print(f"🎯 IPTV.txt 生成完成（含更新时间），共 {len(valid_lines)} 条频道（包含 rtp 和 udp 格式）")

# ===============================
# 文件推送  
def push_all_files():
    print("🚀 推送所有更新文件到 GitHub...")
    os.system('git config --global user.name "github-actions"')
    os.system('git config --global user.email "github-actions@users.noreply.github.com"')
    os.system("git add 计数.txt")
    os.system("git add ip/*.txt || true")
    os.system("git add IPTV.txt || true")
    os.system('git commit -m "自动更新：计数、IP文件、IPTV.txt" || echo "⚠️ 无需提交"')
    os.system("git push origin main || echo '⚠️ 推送失败'")


# ===============================
# 主执行逻辑
if __name__ == "__main__":
    run_count = first_stage()
    if run_count in [12, 24, 36, 48, 60, 72]:
        second_stage()
        third_stage()
    push_all_files()
