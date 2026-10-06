# 参考网页的实测记录

采样日期：2026-10-06。网页：[支付宝 AI 付官网](https://aipay.alipay.com/)。核对方式：公开 HTML/CSS/JS 读取，以及 Chrome 在1440×1000和390×844视口的页面截图与计算样式。网页后续可能变化；这是一份设计快照，不是要求生成时重新下载原站的依赖。

没有证据可以从页面外观、Astro资源名称或“Vibe Pay”产品名，确认网站是否采用 AI/vibe coding 开发。

## 可核查的资源

- [主样式](https://gw.alipayobjects.com/render/p/yuyan/180020010001292425/_astro/home-page.CXllI8Lg.css)
- [导航](https://gw.alipayobjects.com/render/p/yuyan/180020010001292425/_astro/top-bar.BMyWyTuD.css)
- [按钮圆角覆盖](https://gw.alipayobjects.com/render/p/yuyan/180020010001292425/_astro/button-radius.Bax1pI-i.css)
- [命令卡片](https://gw.alipayobjects.com/render/p/yuyan/180020010001292425/_astro/index.DGZozR5a.css)
- [产品轮播样式](https://gw.alipayobjects.com/render/p/yuyan/180020010001292425/_astro/product-hero-carousel.DAaEb_9K.css)
- [主页交互](https://gw.alipayobjects.com/render/p/yuyan/180020010001292425/_astro/home-page.EK9d5sEi.js)
- [轮播交互](https://gw.alipayobjects.com/render/p/yuyan/180020010001292425/_astro/product-hero-carousel.tJQWQGrO.js)

## 静态设计

| 项目 | 原站声明/计算值 | 证据位置 |
| --- | --- | --- |
| 主字体 | 系统无衬线，含 Segoe UI、PingFang SC、Hiragino Sans GB、Microsoft YaHei 等回退 | 主样式 `body` / `--font-system`；浏览器计算样式 |
| 数字 | `Alibaba Sans 102`，700，`tabular-nums`；400/500/700字体声明 | 主样式 `.proofNumber`；仅确认声明，未单独确认实际字体加载 |
| Hero 标题 | `clamp(36px,4.5vw,56px)`、620、1.14；1440px视口计算字号56px | 主样式后段 `.hero .heroCopy h1` |
| 板块标题 | `clamp(28px,3vw,36px)`、620；桌面计算36px | 主样式 section h2 |
| 正文 | 16px；Hero lead 行高1.75 | 主样式与计算样式 |
| 调色板 | `#0c0c0c`、`#5f5f5f`、`#8a8a8a`、`#e8e8e8`、`#f7f7f7`、`#1677ff`、`#eaf3ff`、白色 | 主样式 `:root` |
| 容器 | 外框1440px、导航横 padding46px，正文1160px；常用横 padding `clamp(20px,4vw,48px)` | 导航 `.siteFrame`、主样式 section |
| 当前Hero | 居中单列，标题区域上限760px，说明上限680px；顶部 `clamp(72px,7vw,96px)`、底部48px | 后段 `.hero .heroCopy` 覆盖早期规则 |
| CTA | 高44px、横 padding20px、14px/500；白底描边与黑底白字 | `.heroActions .pill` 与计算样式 |
| 圆角 | 常规卡18px、场景16px、命令内层12px；Hero CTA99px，导航CTA计算999px | 主样式、命令样式、按钮覆盖与计算样式 |
| 导航 | sticky、58px、半透明白底 `#ffffffd6`、20px backdrop blur、极浅底线 | 导航样式；生成默认可简化为纯白 |
| 产品轮播 | stage300px、透视1200px；卡最小宽240px/最小高224px | 产品轮播样式 |
| 留白 | 常规section上 `clamp(88px,10vw,144px)`、下 `clamp(56px,6vw,80px)`；部分产品段再覆盖100px/200px | 主样式；生成规范缩短了长页面节奏 |

源码还保留旧双栏 Hero、22px 堆叠卡和3.2s交换代码。当前首页没有 `#heroSceneSwap`，不把这些残留规则描述为当前主视觉。本 Skill 的22px展示容器是通用化选项。

## 动画与响应式

| 行为 | 原站参数 | 证据 |
| --- | --- | --- |
| 首屏入场 | 标题.85s/上移20px/blur8px；说明.85s/16px/blur6px；CTA .75s/14px；分段延迟 | `.headlineLine`、`.heroLead`、`.heroCopy .heroActions` |
| 滚动入场 | .72s、24px、blur8px；65–95ms组内错开；观察阈值.18、底部rootMargin -18%；只出现一次 | `.reveal`、`initScrollReveal` |
| 通用缓动 | `cubic-bezier(.22,1,.36,1)` | 主样式 |
| 五步流程 | 进度4.8s，停留.8s；完整周期5.6s；节点缩放.96→1.05→1 | `initHeroSkillFlow` |
| 3D轮播 | 转场.65s，结束后停2s；稳定周期约2.65s；中心scale1.06/z96，内侧.96/±10°，外侧.9/±18° | 轮播 `transitionDuration`、`scheduleAuto`、slots |
| 轮播暂停 | 焦点进入和document.hidden暂停；未见hover暂停监听 | 轮播 `handleFocusIn/Out`、`handleVisibility` |
| 品牌带 | 36s线性循环，hover暂停；重复副本aria-hidden | `.partnerRow`、`.logoWall:hover` |
| 计数 | 默认1100ms，easeInOutQuart，首次进入阈值.45后执行 | `runCountUp` |
| 手机Hero | ≤760px流程纵排，≤600px CTA全宽纵排；标题后置规则仍沿用36–56px clamp | 后置媒体查询及选择器优先级 |
| 手机卡片 | 3D轮播仍保持最小240px，裁切相邻卡；部分功能卡在≤960px改为横向scroll-snap | 轮播和billingBento后置样式 |
| 减少动画 | reveal、Hero动画、品牌带、3D与像素效果关闭或不初始化，轮播退成静态网格 | CSS媒体查询与JS条件 |

## 提炼时有意作出的调整

- 保留白底黑字、系统字体、细边线、分级圆角和小面积强调色；替换品牌、内容、数据与素材。
- 将原站的首屏 blur 入场和随滚动淡出改为默认首屏直接可读；正文用轻量 opacity/transform入场。
- 缩短部分板块的大留白；按业务选择页面长度，不复刻整个支付产品矩阵。
- 通用轮播增加hover暂停、手动与暂停控制，并在手机优先使用横滑/静态布局。
- 8–12s步骤周期、600–800ms轮转和72–112px板块节奏都是生成建议，不能当作原站实测值。
- 字体文件、品牌标识、第三方logo、插画、真实业务数字与安装命令不随 Skill 分发。
