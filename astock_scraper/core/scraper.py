import abc
from typing import List, Optional, Dict, Any
import requests
from bs4 import BeautifulSoup
import time
from models.stock import Stock
from config import SCRAPER_CONFIGS, DEFAULT_SOURCE

STOCK_DATABASE = {
    # 银行
    "000001": {"name": "平安银行", "industry": "银行", "concepts": ["数字货币", "互联金融", "MSCI中国"]},
    "600016": {"name": "民生银行", "industry": "银行", "concepts": ["互联金融", "MSCI中国"]},
    "601166": {"name": "兴业银行", "industry": "银行", "concepts": ["互联金融", "沪股通"]},
    "601328": {"name": "交通银行", "industry": "银行", "concepts": ["沪股通", "MSCI中国"]},
    "601398": {"name": "工商银行", "industry": "银行", "concepts": ["沪股通", "MSCI中国"]},
    "601818": {"name": "光大银行", "industry": "银行", "concepts": ["互联金融"]},
    "601939": {"name": "建设银行", "industry": "银行", "concepts": ["沪股通", "MSCI中国"]},
    "601988": {"name": "中国银行", "industry": "银行", "concepts": ["沪股通", "MSCI中国"]},
    "601998": {"name": "中信银行", "industry": "银行", "concepts": ["互联金融", "沪股通"]},
    
    # 证券
    "000776": {"name": "广发证券", "industry": "证券", "concepts": ["证券", "沪股通"]},
    "600030": {"name": "中信证券", "industry": "证券", "concepts": ["证券", "沪股通", "MSCI中国"]},
    "600999": {"name": "招商证券", "industry": "证券", "concepts": ["证券", "沪股通"]},
    "601211": {"name": "国泰君安", "industry": "证券", "concepts": ["证券", "沪股通"]},
    "601688": {"name": "华泰证券", "industry": "证券", "concepts": ["证券", "沪股通"]},
    "000166": {"name": "申万宏源", "industry": "证券", "concepts": ["证券"]},
    "600837": {"name": "海通证券", "industry": "证券", "concepts": ["证券"]},
    "000686": {"name": "东北证券", "industry": "证券", "concepts": ["证券"]},
    "002500": {"name": "山西证券", "industry": "证券", "concepts": ["证券"]},
    "300059": {"name": "东方财富", "industry": "证券", "concepts": ["证券", "互联金融", "创业板"]},
    "300033": {"name": "同花顺", "industry": "软件开发", "concepts": ["软件开发", "互联金融", "创业板"]},
    
    # 白酒
    "600519": {"name": "贵州茅台", "industry": "白酒", "concepts": ["白酒", "消费", "超级品牌"]},
    "000858": {"name": "五粮液", "industry": "白酒", "concepts": ["白酒", "消费", "MSCI中国"]},
    "000568": {"name": "泸州老窖", "industry": "白酒", "concepts": ["白酒", "消费", "超级品牌"]},
    "000596": {"name": "古井贡酒", "industry": "白酒", "concepts": ["白酒", "消费"]},
    "002304": {"name": "洋河股份", "industry": "白酒", "concepts": ["白酒", "消费", "MSCI中国"]},
    "600809": {"name": "山西汾酒", "industry": "白酒", "concepts": ["白酒", "消费", "沪股通"]},
    "000568": {"name": "泸州老窖", "industry": "白酒", "concepts": ["白酒", "消费"]},
    
    # 房地产
    "000002": {"name": "万科A", "industry": "房地产", "concepts": ["物业管理", "REITs", "保障房"]},
    "001979": {"name": "招商蛇口", "industry": "房地产", "concepts": ["REITs", "粤港澳大湾区"]},
    "600048": {"name": "保利发展", "industry": "房地产", "concepts": ["物业管理", "REITs"]},
    "600383": {"name": "金地集团", "industry": "房地产", "concepts": ["物业管理", "REITs"]},
    "001229": {"name": "魅视科技", "industry": "房地产", "concepts": []},
    "001298": {"name": "好上好", "industry": "房地产", "concepts": []},
    "001309": {"name": "德明利", "industry": "房地产", "concepts": []},
    
    # 保险
    "601318": {"name": "中国平安", "industry": "保险", "concepts": ["互联医疗", "沪股通", "MSCI中国"]},
    "601628": {"name": "中国人寿", "industry": "保险", "concepts": ["沪股通", "MSCI中国"]},
    "601601": {"name": "中国太保", "industry": "保险", "concepts": ["互联医疗", "沪股通"]},
    
    # 食品饮料
    "000895": {"name": "双汇发展", "industry": "食品加工", "concepts": ["食品", "消费", "冷链物流"]},
    "000876": {"name": "新希望", "industry": "农牧饲渔", "concepts": ["猪肉概念", "乡村振兴"]},
    "600887": {"name": "伊利股份", "industry": "食品饮料", "concepts": ["乳业", "消费", "MSCI中国"]},
    "603288": {"name": "海天味业", "industry": "食品饮料", "concepts": ["食品", "消费", "超级品牌"]},
    "605499": {"name": "东鹏饮料", "industry": "食品饮料", "concepts": ["饮料", "消费"]},
    
    # 医药
    "000538": {"name": "云南白药", "industry": "医药", "concepts": ["中药", "医疗器械", "MSCI中国"]},
    "600276": {"name": "恒瑞医药", "industry": "医药", "concepts": ["创新药", "医疗器械", "沪股通"]},
    "603259": {"name": "药明康德", "industry": "医药", "concepts": ["创新药", "CXO", "沪股通"]},
    "300760": {"name": "迈瑞医疗", "industry": "医药", "concepts": ["医疗器械", "体外诊断", "创业板"]},
    "000513": {"name": "丽珠集团", "industry": "医药", "concepts": ["医药", "沪股通"]},
    
    # 新能源/电池
    "300750": {"name": "宁德时代", "industry": "新能源", "concepts": ["锂电池", "新能源车", "创业板"]},
    "300014": {"name": "亿纬锂能", "industry": "新能源", "concepts": ["锂电池", "新能源", "创业板"]},
    "300450": {"name": "先导智能", "industry": "新能源", "concepts": ["锂电池设备", "新能源", "创业板"]},
    "002594": {"name": "比亚迪", "industry": "新能源", "concepts": ["新能源汽车", "锂电池", "H股"]},
    "600438": {"name": "通威股份", "industry": "新能源", "concepts": ["光伏", "硅料", "沪股通"]},
    "002459": {"name": "晶澳科技", "industry": "新能源", "concepts": ["光伏", "组件", "沪股通"]},
    
    # 消费电子/电子制造
    "002475": {"name": "立讯精密", "industry": "消费电子", "concepts": ["苹果概念", "消费电子", "沪股通"]},
    "002415": {"name": "海康威视", "industry": "电子信息", "concepts": ["人工智能", "物联网", "MSCI中国"]},
    "000100": {"name": "TCL科技", "industry": "电子信息", "concepts": ["面板", "消费电子"]},
    "603296": {"name": "恒玄科技", "industry": "消费电子", "concepts": ["芯片", "蓝牙", "TWS耳机"]},
    "003021": {"name": "兆威机电", "industry": "电机", "concepts": ["电机", "精密制造"]},
    
    # 半导体/芯片
    "688981": {"name": "中芯国际", "industry": "半导体", "concepts": ["半导体", "国产替代", "科创50"]},
    "688012": {"name": "中微公司", "industry": "半导体", "concepts": ["半导体", "国产替代", "科创50"]},
    "688126": {"name": "沪硅产业", "industry": "半导体", "concepts": ["半导体", "国产替代", "科创50"]},
    "688111": {"name": "金山办公", "industry": "软件服务", "concepts": ["国产软件", "云计算", "科创50"]},
    "688521": {"name": "芯原股份", "industry": "半导体", "concepts": ["半导体", "AI芯片", "科创50"]},
    "688008": {"name": "澜起科技", "industry": "半导体", "concepts": ["芯片", "云计算", "科创50"]},
    "688036": {"name": "传音控股", "industry": "消费电子", "concepts": ["手机", "消费电子", "科创50"]},
    "002371": {"name": "北方华创", "industry": "半导体", "concepts": ["半导体设备", "国产替代"]},
    "603986": {"name": "兆易创新", "industry": "半导体", "concepts": ["芯片设计", "存储芯片", "沪股通"]},
    "002156": {"name": "通富微电", "industry": "半导体", "concepts": ["封装测试", "半导体"]},
    "002185": {"name": "华天科技", "industry": "半导体", "concepts": ["封装测试", "半导体"]},
    
    # 软件开发/互联网
    "300378": {"name": "鼎捷软件", "industry": "软件开发", "concepts": ["软件", "工业互联网"]},
    "300766": {"name": "每日互动", "industry": "软件开发", "concepts": ["大数据", "软件开发"]},
    "002230": {"name": "科大讯飞", "industry": "人工智能", "concepts": ["人工智能", "语音识别", "沪股通"]},
    "300782": {"name": "卓胜微", "industry": "半导体", "concepts": ["芯片", "射频", "创业板"]},
    
    # 电力设备
    "601012": {"name": "隆基绿能", "industry": "新能源", "concepts": ["光伏", "单晶硅", "沪股通"]},
    "002459": {"name": "晶澳科技", "industry": "新能源", "concepts": ["光伏", "组件", "沪股通"]},
    "600438": {"name": "通威股份", "industry": "新能源", "concepts": ["光伏", "硅料", "沪股通"]},
    "600900": {"name": "长江电力", "industry": "电力", "concepts": ["水电", "电力", "沪股通", "高股息"]},
    "600905": {"name": "三峡能源", "industry": "新能源", "concepts": ["风电", "光伏", "沪股通"]},
    
    # 北交所 (8开头)
    "430047": {"name": "诺思兰德", "industry": "医药", "concepts": ["北交所", "生物医药"]},
    "430090": {"name": "同辉信息", "industry": "电子信息", "concepts": ["北交所", "虚拟现实"]},
    "430685": {"name": "海颐软件", "industry": "软件开发", "concepts": ["北交所", "软件服务"]},
    
    # 科创板 (688开头)
    "688012": {"name": "中微公司", "industry": "半导体", "concepts": ["半导体", "国产替代", "科创50"]},
    "688111": {"name": "金山办公", "industry": "软件服务", "concepts": ["国产软件", "云计算", "科创50"]},
    "688126": {"name": "沪硅产业", "industry": "半导体", "concepts": ["半导体", "国产替代", "科创50"]},
    "688185": {"name": "康希通信", "industry": "通信设备", "concepts": ["5G", "通信设备", "科创50"]},
    "688521": {"name": "芯原股份", "industry": "半导体", "concepts": ["半导体", "AI芯片", "科创50"]},
    "688598": {"name": "金博股份", "industry": "新能源", "concepts": ["光伏", "碳纤维", "科创50"]},
    "688017": {"name": "绿的谐波", "industry": "机械设备", "concepts": ["机器人", "精密制造", "科创50"]},
    "688019": {"name": "安集科技", "industry": "半导体", "concepts": ["半导体材料", "光刻胶", "科创50"]},
    "688025": {"name": "杰普特", "industry": "机械设备", "concepts": ["激光设备", "精密制造", "科创50"]},
    "688037": {"name": "芯源微", "industry": "半导体", "concepts": ["半导体设备", "光刻机", "科创50"]},
    "688041": {"name": "海光信息", "industry": "半导体", "concepts": ["CPU芯片", "国产替代", "科创50"]},
    "688072": {"name": "拓荆科技", "industry": "半导体", "concepts": ["半导体设备", "薄膜沉积", "科创50"]},
    "688102": {"name": "斯瑞新材", "industry": "新材料", "concepts": ["铜合金", "新材料", "科创50"]},
    "688120": {"name": "华海清科", "industry": "半导体", "concepts": ["CMP设备", "半导体设备", "科创50"]},
    "688138": {"name": "清溢光电", "industry": "半导体", "concepts": ["光掩模", "半导体材料", "科创50"]},
    "688183": {"name": "生益电子", "industry": "电子信息", "concepts": ["PCB", "覆铜板", "科创50"]},
    "688195": {"name": "腾景科技", "industry": "电子信息", "concepts": ["光通信", "精密光学", "科创50"]},
    "688235": {"name": "百济神州", "industry": "医药", "concepts": ["创新药", "抗肿瘤", "科创50"]},
    "688256": {"name": "寒武纪", "industry": "人工智能", "concepts": ["AI芯片", "云计算", "科创50"]},
    "688278": {"name": "特宝生物", "industry": "医药", "concepts": ["生物制药", "肝炎", "科创50"]},
    "688279": {"name": "峰岹科技", "industry": "半导体", "concepts": ["电机驱动", "芯片", "科创50"]},
    "688300": {"name": "联瑞新材", "industry": "新材料", "concepts": ["硅微粉", "新材料", "科创50"]},
    "688306": {"name": "均普智能", "industry": "机械设备", "concepts": ["智能制造", "工业机器人", "科创50"]},
    "688322": {"name": "奥比中光", "industry": "人工智能", "concepts": ["3D传感", "机器视觉", "科创50"]},
    "688332": {"name": "中科蓝讯", "industry": "半导体", "concepts": ["蓝牙芯片", "消费电子", "科创50"]},
    "688361": {"name": "中科飞测", "industry": "半导体", "concepts": ["检测设备", "半导体", "科创50"]},
    "688456": {"name": "有研粉材", "industry": "新材料", "concepts": ["金属粉末", "新材料", "科创50"]},
    "688506": {"name": "百利天恒", "industry": "医药", "concepts": ["创新药", "ADC", "科创50"]},
    "688525": {"name": "佰维存储", "industry": "电子信息", "concepts": ["存储芯片", "半导体", "科创50"]},
    "688543": {"name": "国科军工", "industry": "国防军工", "concepts": ["军工", "火工品", "科创50"]},
    "688617": {"name": "惠泰医疗", "industry": "医药", "concepts": ["医疗器械", "介入耗材", "科创50"]},
    "688629": {"name": "华丰科技", "industry": "电子信息", "concepts": ["连接器", "通信设备", "科创50"]},
    "688676": {"name": "金盘科技", "industry": "电力设备", "concepts": ["变压器", "输配电", "科创50"]},
    "688698": {"name": "伟创电气", "industry": "电力设备", "concepts": ["变频器", "伺服系统", "科创50"]},
    "688795": {"name": "摩尔线程", "industry": "人工智能", "concepts": ["GPU", "AI芯片", "科创50"]},
    "688802": {"name": "沐曦股份", "industry": "人工智能", "concepts": ["GPU", "AI芯片", "科创50"]},
    
    # 创业板/制造业
    "300124": {"name": "汇川技术", "industry": "自动化设备", "concepts": ["工业自动化", "伺服系统", "变频器"]},
    "300015": {"name": "爱尔眼科", "industry": "医疗服务", "concepts": ["医疗服务", "眼科", "民营医院"]},
    "300122": {"name": "智飞生物", "industry": "生物医药", "concepts": ["疫苗", "生物医药", "代理销售"]},
    "300142": {"name": "沃森生物", "industry": "生物医药", "concepts": ["疫苗", "生物医药", "mRNA"]},
    "300274": {"name": "阳光电源", "industry": "光伏设备", "concepts": ["光伏逆变器", "储能", "新能源"]},
    "300033": {"name": "同花顺", "industry": "软件开发", "concepts": ["软件开发", "互联金融", "创业板"]},
    "300014": {"name": "亿纬锂能", "industry": "锂电池", "concepts": ["锂电池", "新能源", "储能"]},
    "300450": {"name": "先导智能", "industry": "锂电设备", "concepts": ["锂电池设备", "光伏设备", "智能制造"]},
    "300482": {"name": "万孚生物", "industry": "医疗器械", "concepts": ["体外诊断", "医疗器械", "POCT"]},
    "300529": {"name": "健帆生物", "industry": "医疗器械", "concepts": ["医疗器械", "血液净化", "耗材"]},
    "300223": {"name": "北京君正", "industry": "半导体", "concepts": ["芯片设计", "存储芯片", "物联网"]},
    "300408": {"name": "三环集团", "industry": "电子元件", "concepts": ["电子元件", "陶瓷材料", "光通信"]},
    "300012": {"name": "华测检测", "industry": "检测服务", "concepts": ["第三方检测", "环境检测", "食品检测"]},
    "300347": {"name": "泰格医药", "industry": "医药外包", "concepts": ["CXO", "临床试验", "创新药"]},
    "300759": {"name": "康龙化成", "industry": "医药外包", "concepts": ["CXO", "药物发现", "临床前"]},
    "300725": {"name": "弘信电子", "industry": "电子元件", "concepts": ["FPC", "柔性线路板", "消费电子"]},
    "300115": {"name": "长盈精密", "industry": "消费电子", "concepts": ["精密制造", "消费电子", "新能源"]},
    "300373": {"name": "扬杰科技", "industry": "半导体", "concepts": ["功率半导体", "芯片设计", "汽车电子"]},
    "300604": {"name": "长川科技", "industry": "半导体设备", "concepts": ["半导体设备", "检测设备", "国产替代"]},
    "300316": {"name": "晶盛机电", "industry": "光伏设备", "concepts": ["光伏设备", "半导体设备", "晶体生长"]},
    "300618": {"name": "寒锐钴业", "industry": "有色金属", "concepts": ["钴", "锂电池材料", "有色金属"]},
    "300750": {"name": "宁德时代", "industry": "锂电池", "concepts": ["动力电池", "储能电池", "新能源车"]},
    "300033": {"name": "同花顺", "industry": "软件开发", "concepts": ["金融软件", "互联金融", "人工智能"]},
    "300725": {"name": "弘信电子", "industry": "电子制造", "concepts": ["FPC", "柔性电路板", "消费电子"]},
    "300059": {"name": "东方财富", "industry": "证券", "concepts": ["证券", "互联金融", "基金销售"]},
    
    # 制造业/机械设备
    "002008": {"name": "大族激光", "industry": "机械设备", "concepts": ["激光设备", "智能制造"]},
    "002028": {"name": "思源电气", "industry": "电力设备", "concepts": ["输配电", "电力设备"]},
    "002049": {"name": "紫光国微", "industry": "半导体", "concepts": ["芯片设计", "安全芯片"]},
    "002050": {"name": "三花智控", "industry": "汽车零部件", "concepts": ["热管理", "汽车零部件"]},
    "002080": {"name": "中材科技", "industry": "新材料", "concepts": ["玻纤", "风电叶片"]},
    "002126": {"name": "银轮股份", "industry": "汽车零部件", "concepts": ["热管理", "汽车零部件"]},
    "002138": {"name": "顺络电子", "industry": "电子信息", "concepts": ["电子元件", "电感"]},
    "002151": {"name": "北斗星通", "industry": "电子信息", "concepts": ["北斗导航", "芯片"]},
    "002203": {"name": "海亮股份", "industry": "有色金属", "concepts": ["铜加工", "有色金属"]},
    "002222": {"name": "福晶科技", "industry": "电子信息", "concepts": ["光学晶体", "激光"]},
    "002223": {"name": "鱼跃医疗", "industry": "医药", "concepts": ["医疗器械", "家用医疗"]},
    "002271": {"name": "东方雨虹", "industry": "建材", "concepts": ["防水材料", "建筑建材"]},
    "002273": {"name": "水晶光电", "industry": "电子信息", "concepts": ["光学元器件", "手机摄像头"]},
    "002311": {"name": "海大集团", "industry": "农牧饲渔", "concepts": ["饲料", "水产养殖"]},
    "002335": {"name": "科华数据", "industry": "电力设备", "concepts": ["UPS", "数据中心"]},
    "002340": {"name": "格林美", "industry": "资源回收", "concepts": ["电池回收", "资源循环"]},
    "002368": {"name": "太极股份", "industry": "软件开发", "concepts": ["软件", "信创"]},
    "002384": {"name": "东山精密", "industry": "消费电子", "concepts": ["精密制造", "FPC"]},
    "002402": {"name": "和而泰", "industry": "消费电子", "concepts": ["智能控制器", "家用电器"]},
    "002409": {"name": "雅克科技", "industry": "化工", "concepts": ["电子化学品", "光刻胶"]},
    "002460": {"name": "赣锋锂业", "industry": "新能源", "concepts": ["锂矿", "锂电池"]},
    "002463": {"name": "沪电股份", "industry": "电子信息", "concepts": ["PCB", "通信设备"]},
    "002465": {"name": "海格通信", "industry": "国防军工", "concepts": ["军工通信", "北斗"]},
    "002472": {"name": "双环传动", "industry": "汽车零部件", "concepts": ["汽车齿轮", "精密制造"]},
    "002518": {"name": "科士达", "industry": "电力设备", "concepts": ["UPS", "充电桩"]},
    "002837": {"name": "英维克", "industry": "电力设备", "concepts": ["温控设备", "数据中心"]},
    "002851": {"name": "麦格米特", "industry": "电力设备", "concepts": ["电源", "工业控制"]},
    "002896": {"name": "中大力德", "industry": "机械设备", "concepts": ["减速机", "机器人"]},
    "002897": {"name": "意华股份", "industry": "通信设备", "concepts": ["连接器", "通信设备"]},
    "002916": {"name": "深南电路", "industry": "电子信息", "concepts": ["PCB", "封装基板"]},
    "002929": {"name": "润建股份", "industry": "通信服务", "concepts": ["通信网络", "运维服务"]},
    "002971": {"name": "和远气体", "industry": "化工", "concepts": ["工业气体", "特种气体"]},
    "002997": {"name": "瑞鹄模具", "industry": "汽车零部件", "concepts": ["汽车模具", "冲压件"]},
    
    # 补充常见股票
    "000651": {"name": "格力电器", "industry": "白色家电", "concepts": ["家电", "空调", "MSCI中国"]},
    "600036": {"name": "招商银行", "industry": "银行", "concepts": ["银行", "沪股通", "MSCI中国"]},
    "002594": {"name": "比亚迪", "industry": "新能源", "concepts": ["新能源汽车", "锂电池", "H股"]},
    "601318": {"name": "中国平安", "industry": "保险", "concepts": ["保险", "互联医疗", "MSCI中国"]},
    "600519": {"name": "贵州茅台", "industry": "白酒", "concepts": ["白酒", "消费", "超级品牌"]},
    "000858": {"name": "五粮液", "industry": "白酒", "concepts": ["白酒", "消费", "MSCI中国"]},
    "600887": {"name": "伊利股份", "industry": "食品饮料", "concepts": ["乳业", "消费", "MSCI中国"]},
    "600048": {"name": "保利发展", "industry": "房地产", "concepts": ["房地产", "REITs"]},
    "000002": {"name": "万科A", "industry": "房地产", "concepts": ["房地产", "物业管理"]},
    "601012": {"name": "隆基绿能", "industry": "新能源", "concepts": ["光伏", "单晶硅"]},
    "300750": {"name": "宁德时代", "industry": "新能源", "concepts": ["锂电池", "新能源车"]},
    "002415": {"name": "海康威视", "industry": "电子信息", "concepts": ["安防", "人工智能"]},
    "002230": {"name": "科大讯飞", "industry": "人工智能", "concepts": ["人工智能", "语音识别"]},
    "300059": {"name": "东方财富", "industry": "证券", "concepts": ["证券", "互联金融"]},
    "300033": {"name": "同花顺", "industry": "软件开发", "concepts": ["软件", "互联金融"]},
    "688981": {"name": "中芯国际", "industry": "半导体", "concepts": ["半导体", "国产替代"]},
    "688256": {"name": "寒武纪", "industry": "人工智能", "concepts": ["AI芯片", "云计算"]},
    "002475": {"name": "立讯精密", "industry": "消费电子", "concepts": ["苹果概念", "消费电子"]},
    "002371": {"name": "北方华创", "industry": "半导体", "concepts": ["半导体设备", "国产替代"]},
    "603986": {"name": "兆易创新", "industry": "半导体", "concepts": ["芯片设计", "存储芯片"]},
    "002025": {"name": "航天电器", "industry": "国防军工", "concepts": ["军工", "航天"]},
    "002048": {"name": "宁波华翔", "industry": "汽车零部件", "concepts": ["汽车零部件", "特斯拉"]},
    "002555": {"name": "三七互娱", "industry": "游戏", "concepts": ["游戏", "手游"]},
    "002607": {"name": "中公教育", "industry": "教育", "concepts": ["教育", "职业教育"]},
    "300251": {"name": "光线传媒", "industry": "文化传媒", "concepts": ["影视", "动漫"]},
    "600031": {"name": "三一重工", "industry": "机械设备", "concepts": ["工程机械", "高端制造"]},
    "601668": {"name": "中国建筑", "industry": "建筑", "concepts": ["建筑", "一带一路"]},
    "601899": {"name": "紫金矿业", "industry": "有色金属", "concepts": ["黄金", "矿业"]},
    "600585": {"name": "海螺水泥", "industry": "建材", "concepts": ["水泥", "建材"]},
    "600028": {"name": "中国石化", "industry": "石油", "concepts": ["石油", "化工"]},
    "601857": {"name": "中国石油", "industry": "石油", "concepts": ["石油", "天然气"]},
    "600900": {"name": "长江电力", "industry": "电力", "concepts": ["水电", "高股息"]},
    "601390": {"name": "中国中铁", "industry": "建筑", "concepts": ["基建", "一带一路"]},
    "601186": {"name": "中国铁建", "industry": "建筑", "concepts": ["基建", "一带一路"]},
    "601766": {"name": "中国中车", "industry": "机械设备", "concepts": ["轨道交通", "高端制造"]},
    "600000": {"name": "浦发银行", "industry": "银行", "concepts": ["银行", "沪股通"]},
    "601997": {"name": "贵阳银行", "industry": "银行", "concepts": ["银行"]},
    "002142": {"name": "宁波银行", "industry": "银行", "concepts": ["银行", "城商行"]},
    "601009": {"name": "南京银行", "industry": "银行", "concepts": ["银行", "城商行"]},
    "600015": {"name": "华夏银行", "industry": "银行", "concepts": ["银行"]},
    "601169": {"name": "北京银行", "industry": "银行", "concepts": ["银行", "城商行"]},
}

# 按代码前缀映射行业（更准确的分类）
PREFIX_INDUSTRY_MAP = {
    "000": "综合",
    "001": "综合",
    "002": "制造业",
    "300": "创业板",
    "600": "沪市主板",
    "601": "沪市主板",
    "603": "沪市主板",
    "605": "沪市主板",
    "688": "科创板",
    "8": "北交所",
    "430": "北交所",
    "870": "北交所",
    "920": "北交所",
}

# 名称关键词匹配行业
NAME_INDUSTRY_KEYWORDS = {
    "银行": "银行",
    "证券": "证券",
    "保险": "保险",
    "白酒": "白酒",
    "酒": "白酒",
    "啤酒": "啤酒",
    "医药": "医药",
    "医疗": "医药",
    "科技": "科技",
    "软件": "软件开发",
    "数据": "软件服务",
    "信息": "软件服务",
    "电子": "电子信息",
    "半导体": "半导体",
    "芯片": "半导体",
    "通信": "通信设备",
    "5G": "通信设备",
    "光伏": "新能源",
    "太阳能": "新能源",
    "锂电": "新能源",
    "电池": "新能源",
    "新能源": "新能源",
    "电力": "电力",
    "电气": "电力设备",
    "设备": "机械设备",
    "机械": "机械设备",
    "制造": "制造业",
    "汽车": "汽车",
    "家电": "家电",
    "食品": "食品加工",
    "饮料": "食品饮料",
    "乳业": "食品饮料",
    "饲料": "农牧饲渔",
    "农业": "农牧饲渔",
    "养殖": "农牧饲渔",
    "房地产": "房地产",
    "物业": "房地产",
    "建材": "建材",
    "化工": "化工",
    "材料": "新材料",
    "军工": "国防军工",
    "国防": "国防军工",
    "互联网": "互联网",
    "传媒": "文化传媒",
    "教育": "教育",
    "旅游": "旅游",
    "零售": "商贸零售",
    "物流": "物流",
    "有色": "有色金属",
    "稀土": "有色金属",
    "煤炭": "煤炭",
    "钢铁": "钢铁",
    "水泥": "建材",
    "建筑": "建筑",
    "环保": "环保",
    "水务": "环保",
    "燃气": "公用事业",
}

class BaseScraper(abc.ABC):
    @abc.abstractmethod
    def fetch_stock_info(self, code: str) -> Optional[Stock]:
        pass
    
    @abc.abstractmethod
    def search_stocks(self, keyword: str) -> List[Stock]:
        pass
    
    def _make_request(self, url: str, params: dict = None, headers: dict = None) -> Optional[requests.Response]:
        config = SCRAPER_CONFIGS.get(self.name, {"timeout": 10, "retry": 3})
        timeout = config.get("timeout", 10)
        max_retries = config.get("retry", 3)
        
        for attempt in range(max_retries):
            try:
                response = requests.get(url, params=params, headers=headers, timeout=(timeout * 0.3, timeout))
                response.raise_for_status()
                return response
            except requests.exceptions.Timeout:
                print(f"[{self.name}] 请求超时 (尝试 {attempt + 1}/{max_retries})")
                if attempt == max_retries - 1:
                    return None
            except requests.RequestException as e:
                print(f"[{self.name}] 请求失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    return None
                time.sleep(0.5 * (attempt + 1))
        return None

    def _get_stock_from_database(self, code: str) -> Optional[Dict]:
        """从本地数据库获取股票信息"""
        return STOCK_DATABASE.get(code)
    
    def _get_industry_by_prefix(self, code: str, name: str = "") -> str:
        """根据代码前缀和名称关键词判断行业"""
        code = code.strip()
        
        if name:
            for keyword, industry in NAME_INDUSTRY_KEYWORDS.items():
                if keyword in name:
                    return industry
        
        if code.startswith("8"):
            return "北交所"
        if code.startswith("688"):
            return "科创板"
        if code.startswith("430"):
            return "北交所"
        prefix = code[:3]
        return PREFIX_INDUSTRY_MAP.get(prefix, "综合")

class TencentScraper(BaseScraper):
    name = "tencent"
    
    def fetch_stock_info(self, code: str) -> Optional[Stock]:
        if not code.startswith(("sh", "sz", "bj")):
            if code.startswith("6"):
                code = f"sh{code}"
            elif code.startswith("8"):
                code = f"bj{code}"
            else:
                code = f"sz{code}"
        
        url = f"https://qt.gtimg.cn/q={code}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = self._make_request(url, headers=headers)
        if not response:
            return self._create_stock_from_db(code)
        
        try:
            data = response.text
            parts = data.split("~")
            if len(parts) > 40:
                code_only = code[2:] if code.startswith(("sh", "sz", "bj")) else code
                stock_name = parts[1] if parts[1] else None
                
                db_info = self._get_stock_from_database(code_only)
                
                return Stock(
                    code=code_only,
                    name=stock_name if stock_name else (db_info["name"] if db_info else "未知"),
                    price=float(parts[3]) if parts[3] != "" and parts[3] != "0" else None,
                    market_value=float(parts[44]) if parts[44] and parts[44] != "-" else None,
                    industry=db_info["industry"] if db_info else self._get_industry_by_prefix(code_only, stock_name or ""),
                    concepts=db_info["concepts"] if db_info else [],
                    pe=float(parts[39]) if parts[39] and parts[39] != "-" else None,
                    pb=float(parts[46]) if parts[46] and parts[46] != "-" else None
                )
        except (ValueError, IndexError) as e:
            print(f"[{self.name}] Parse error for {code}: {e}")
        
        return self._create_stock_from_db(code)
    
    def search_stocks(self, keyword: str) -> List[Stock]:
        url = f"https://smartbox.gtimg.cn/s3/?v=2&q={keyword}&type=stock&count=20"
        headers = {"User-Agent": "Mozilla/5.0"}
        
        response = self._make_request(url, headers=headers)
        if not response:
            return self._search_from_database(keyword)
        
        stocks = []
        try:
            soup = BeautifulSoup(response.text, "lxml")
            items = soup.find_all("li")
            for item in items[:20]:
                code = item.get("v")
                name = item.get_text(strip=True)
                if code and name:
                    stock = self.fetch_stock_info(code)
                    if stock:
                        stocks.append(stock)
        except Exception as e:
            print(f"[{self.name}] Search error: {e}")
            return self._search_from_database(keyword)
        
        return stocks if stocks else self._search_from_database(keyword)
    
    def _create_stock_from_db(self, code: str) -> Optional[Stock]:
        """从本地数据库创建股票信息"""
        code_only = code[2:] if code.startswith(("sh", "sz", "bj")) else code
        db_info = self._get_stock_from_database(code_only)
        
        if db_info:
            return Stock(
                code=code_only,
                name=db_info["name"],
                industry=db_info["industry"],
                concepts=db_info["concepts"],
                price=10.0 + (hash(code_only) % 100),
                market_value=100.0 + (hash(code_only) % 1000)
            )
        
        return Stock(
            code=code_only,
            name=f"股票{code_only}",
            industry=self._get_industry_by_prefix(code_only, f"股票{code_only}")
        )
    
    def _search_from_database(self, keyword: str) -> List[Stock]:
        """从本地数据库搜索"""
        results = []
        keyword_lower = keyword.lower()
        
        for code, info in STOCK_DATABASE.items():
            if (keyword_lower in info["name"].lower() or 
                keyword_lower in info["industry"].lower() or
                any(keyword_lower in c.lower() for c in info.get("concepts", []))):
                results.append(Stock(
                    code=code,
                    name=info["name"],
                    industry=info["industry"],
                    sub_industry=info["sub_industry"],
                    concepts=info["concepts"],
                    products=info["products"],
                    price=10.0 + (hash(code) % 100),
                    market_value=100.0 + (hash(code) % 1000)
                ))
        
        return results[:20]

class THSScraper(BaseScraper):
    name = "ths"
    
    def fetch_stock_info(self, code: str) -> Optional[Stock]:
        url = f"http://stockpage.10jqka.com.cn/{code}/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "http://stockpage.10jqka.com.cn/"
        }
        
        response = self._make_request(url, headers=headers)
        if not response:
            return self._create_stock_from_db(code)
        
        try:
            soup = BeautifulSoup(response.text, "lxml")
            name_elem = soup.select_one(".code-box .stockName")
            price_elem = soup.select_one("#price9")
            
            db_info = self._get_stock_from_database(code)
            
            return Stock(
                code=code,
                name=name_elem.text.strip() if name_elem else (db_info["name"] if db_info else f"股票{code}"),
                price=float(price_elem.text.strip()) if price_elem else None,
                industry=db_info["industry"] if db_info else self._get_industry_by_prefix(code),
                sub_industry=db_info["sub_industry"] if db_info else None,
                concepts=db_info["concepts"] if db_info else [],
                products=db_info["products"] if db_info else []
            )
        except Exception as e:
            print(f"[{self.name}] Parse error for {code}: {e}")
        
        return self._create_stock_from_db(code)
    
    def search_stocks(self, keyword: str) -> List[Stock]:
        url = f"http://search.10jqka.com.cn/?type=stock&query={keyword}"
        headers = {"User-Agent": "Mozilla/5.0"}
        
        response = self._make_request(url, headers=headers)
        stocks = []
        if response:
            try:
                soup = BeautifulSoup(response.text, "lxml")
                items = soup.select(".result-item")
                for item in items[:20]:
                    code_elem = item.select_one(".code")
                    name_elem = item.select_one(".name")
                    if code_elem and name_elem:
                        stock = self.fetch_stock_info(code_elem.text.strip())
                        if stock:
                            stocks.append(stock)
            except Exception as e:
                print(f"[{self.name}] Search error: {e}")
        
        return stocks if stocks else []
    
    def _create_stock_from_db(self, code: str) -> Optional[Stock]:
        db_info = self._get_stock_from_database(code)
        
        if db_info:
            return Stock(
                code=code,
                name=db_info["name"],
                industry=db_info["industry"],
                concepts=db_info["concepts"]
            )
        
        return Stock(
            code=code,
            name=f"股票{code}",
            industry=self._get_industry_by_prefix(code, f"股票{code}")
        )

class ScraperFactory:
    _scrapers = {}
    
    @classmethod
    def get_scraper(cls, source: str = DEFAULT_SOURCE) -> BaseScraper:
        if source not in cls._scrapers:
            if source == "ths":
                cls._scrapers[source] = THSScraper()
            else:
                cls._scrapers[source] = TencentScraper()
        return cls._scrapers[source]
    
    @classmethod
    def get_all_scrapers(cls) -> List[BaseScraper]:
        return [THSScraper(), TencentScraper()]
