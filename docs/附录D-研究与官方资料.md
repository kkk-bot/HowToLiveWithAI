# 附录 D · 研究与官方资料

按问题查来源即可，不必把资料库当作必读课程。保留 R01—R41 的 41 个记录编号与讲义 L01；R16、R34 是同一报告的不同阅读入口，不重复当成独立证据。

每条只列书目信息、阅读用途、已读范围和关键限制。既有核查主要在 2026-10-10—12 完成；R25、R30、R11 于 2026-10-14 回看，R35—R41 于 2026-10-18 增补。未回看的记录保留原阅读范围。详细取舍见[既有核查记录](https://github.com/kkk-bot/HowToLiveWithAI/blob/main/docs/维护/附录D-详细核查记录-v0.17.2.md)与[本轮文献核查](维护/文献增补与引用核查-v0.19.1.md)。

<a id="d-1"></a>

## D.1 模型原理、检索与训练

<a id="r25"></a>

### R25 · Google Cloud 生成式 AI 术语表

入门术语入口：生成式 AI、模型、上下文、提示词、RAG 与工具调用。适合配合第 1 章查词。

**阅读范围：** 已读相关词条；2026-10-14 回看术语页。入门示例由本项目编写，不采用产品容量与效果宣传。

[官方术语表](https://docs.cloud.google.com/docs/generative-ai/glossary)

<a id="r26"></a>

### R26 · Google Cloud 的生成式 AI 能力、限制与责任说明

理解生成回答的事实错误与使用限制，配合 1.2、1.4 节阅读。

**阅读范围：** 已读相关官方说明；未测试具体产品，也未验证本项目练习效果。

[官方说明](https://docs.cloud.google.com/gemini/docs/discover/responsible-ai?hl=en)

<a id="r27"></a>

### R27 · Transformer 原始论文

Transformer 原始论文，想理解注意力、编码器与解码器时选读第 3 节。

**阅读范围：** 已读第 3 节相关架构说明；未审查全部实验和附录。

[作者论文](https://arxiv.org/abs/1706.03762) · [正文第 3 节](https://arxiv.org/html/1706.03762v7)

<a id="r28"></a>

### R28 · BERT 的双向上下文与预训练

用 BERT 认识双向上下文、预训练与微调，配合附录 A。

**阅读范围：** 已读第 3 节相关内容；该模型的训练目标不能套用于所有模型。

[作者论文](https://arxiv.org/abs/1810.04805) · [正文第 3 节](https://arxiv.org/html/1810.04805v2)

<a id="r29"></a>

### R29 · 检索增强生成原始研究

检索与生成怎样组合的原始研究，适合理解 1.3 节的 RAG。

**阅读范围：** 只读作者摘要与版本信息，未核查全文实验；本项目文件练习不是原研究复现。

[作者摘要与论文入口](https://arxiv.org/abs/2005.11401)

<a id="r30"></a>

### R30 · 工具调用与对话状态的官方说明

工具调用流程：模型提出函数及参数，应用执行并返回结果，配合 1.3、6.2 节。

**阅读范围：** 已读相关官方流程；2026-10-14 回看页面，未运行示例或测试产品。

[Google AI for Developers：Function calling with the Gemini API](https://ai.google.dev/gemini-api/docs/function-calling)

<a id="r31"></a>

### R31 · 训练数据中的原文可能被提取

说明模型可能保留并输出训练数据中的原文，配合 6.1 节。

**阅读范围：** 只读作者摘要；原实验针对 GPT-2，不能估计当前服务的私密资料泄漏概率。

[作者摘要与论文入口](https://arxiv.org/abs/2012.07805)

<a id="r32"></a>

### R32 · 模型坍塌的作者预印本

在特定递归训练设置下讨论模型坍塌，配合 A.5。

**阅读范围：** 已读预印本 v3 的摘要及部分正文；正式发表与更正未核实，不推出所有模型必然坍塌。

[作者预印本 v3](https://arxiv.org/abs/2305.17493v3) · [正文](https://arxiv.org/html/2305.17493v3)

<a id="r33"></a>

### R33 · 保留并累积数据的另一种训练设置

比较保留、累积数据的训练设置，与 R32 对照阅读。

**阅读范围：** 只读作者摘要，未审查全文；不推出所有合成数据有害或保留数据一定安全。

[作者摘要与论文入口](https://arxiv.org/abs/2404.01413)

<a id="r35"></a>

### R35 · 固定流程与 Agent 的区别

Anthropic 的工程文章区分预设步骤与模型动态选择步骤，建议按任务需要增加复杂性。配合正文 1.3、附录 A.4 阅读。

**阅读范围：** 2026-10-18 已读概念区分、使用条件与执行反馈相关正文；属于厂商工程经验，不是普通人学习效果的实验。

[原文](https://www.anthropic.com/engineering/building-effective-agents)

<a id="r37"></a>

### R37 · 长上下文：放得下不等于用得好

Liu 等（2024），Lost in the Middle: How Language Models Use Long Contexts，TACL 12：157—173。用于 1.2 节，解释信息位置会影响特定模型的表现。

**阅读范围：** 2026-10-18 已读摘要及原论文任务设置、结果与结论；测试的是历史模型，不推算当前产品的错误率。

[论文与 DOI](https://aclanthology.org/2024.tacl-1.9/) · [原论文](https://aclanthology.org/2024.tacl-1.9.pdf)

<a id="d-2"></a>

## D.2 任务效果与核查

<a id="r01"></a>

### R01 · 短篇职业写作：AI 可以提高特定任务效率

短篇职业写作实验，支持观察具体任务的时间与质量，配合 2.1、2.5 节。

**阅读范围：** 只读期刊摘要与 MIT 介绍；不将实验效果换成通用提效或工资承诺。

[原始发布资料](https://doi.org/10.1126/science.adh2586) · [补充入口](https://economics.mit.edu/news/study-finds-chatgpt-boosts-worker-productivity-some-writing-tasks)

<a id="r02"></a>

### R02 · 客服现场：不同经验的人收益不同

客服现场研究显示收益因经验而异，配合第 2、5 章。

**阅读范围：** 只读 2024-11 修订版摘要；不混用早期版本的样本与效果数字。

[原始发布资料](https://arxiv.org/abs/2304.11771v2) · [补充入口](https://www.nber.org/papers/w31161)

<a id="r03"></a>

### R03 · 咨询任务：AI 的能力边界因任务而异

咨询任务实验说明能力边界因任务而异，配合 1.4、2.5 节。

**阅读范围：** 已读 HBS 介绍；论文全文及正式发表版本未核查，暂不引用精确效果数字。

[原始发布资料](https://aiinstitute.hbs.edu/navigating-the-jagged-technological-frontier/) · [补充入口](https://aiinstitute.hbs.edu/back-to-the-beginnings-of-ai-at-work/)

<a id="r04"></a>

### R04 · 编程反例：感觉更快，实测可能更慢

熟练开发者的编程试验提供“感觉快、完成却更慢”的反例，配合 2.5 节。

**阅读范围：** 已读试验摘要与机构说明；限于当时工具、参与者和任务，不能预测现在全部编程效果。

[原始发布资料](https://arxiv.org/abs/2507.09089) · [补充入口](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/)

<a id="r05"></a>

### R05 · 编程研究更新：后续测量出现选择偏差

R04 的后续测量更新，帮助理解选择偏差与效果不确定性。

**阅读范围：** 已读研究更新说明；作者未能可靠确定当前效果大小，不补写通用结论。

[原始发布资料](https://metr.org/blog/2026-02-24-uplift-update/)

<a id="r11"></a>

### R11 · 使用风险：核对来源、记录边界与持续检查

NIST 生成式 AI 风险框架，查来源、核对事实时可看第 2.2 节与 MS-2.5-003。

**阅读范围：** 已读相关章节；2026-10-14 回看官方 PDF。本指南的个人流程是改编，未验证全部错误都能被发现。

[原始发布资料](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)

<a id="r38"></a>

### R38 · 模型的赞同不等于事实确认

Sharma 等，Towards Understanding Sycophancy in Language Models，ICLR 2024。用于 2.3 节，讨论模型顺着用户观点回答的风险。

**阅读范围：** 2026-10-18 核对会议摘要，并读作者 v4 的第 2—4、6 节；五种历史助手的测试不等于所有现用工具的表现，也未验证本指南的应对提示。

[会议记录](https://proceedings.iclr.cc/paper_files/paper/2024/hash/0105f7972202c1d4fb817da9f21a9663-Abstract-Conference.html) · [作者 v4](https://arxiv.org/html/2310.13548v4)

<a id="r40"></a>

### R40 · 人机协作：评价结果要看比较基准

Vaccaro、Almaatouq 与 Malone（2024），When combinations of humans and AI are useful: A systematic review and meta-analysis，Nature Human Behaviour。用于 2.5 节。

**阅读范围：** 2026-10-18 已读摘要、总体结果、纳入标准与局限。106 项实验涵盖多类 AI，不能当作当前生成式工具的统一结论；比较基准不同，解释也不同。

[论文全文与 DOI](https://www.nature.com/articles/s41562-024-02024-1)

<a id="d-3"></a>

## D.3 学习与基础技能

<a id="r06"></a>

### R06 · 学习：完成练习不等于独立掌握

高中数学实验区分辅助完成与独立掌握，配合 3.4 节。

**阅读范围：** 已读检索返回的方法与结论，全文访问受限；不能推广到所有学科与人群。

[原始发布资料](https://doi.org/10.1073/pnas.2422633122) · [补充入口](https://github.com/obastani/GenAICanHarmLearning)

<a id="r10"></a>

### R10 · AI 素养：学习内容不止工具操作

UNESCO 学生 AI 素养框架，提供技术、伦理与人本等学习维度。

**阅读范围：** 只读官方介绍页；成人技能分组与顺序由本项目设计，不是就业效果研究。

[原始发布资料](https://www.unesco.org/en/articles/ai-competency-framework-students)

<a id="r22"></a>

### R22 · How AI Impacts Skill Formation

新编程库的短时实验，说明交付任务与独立测验需要分别观察，配合 3.4 节。

**阅读范围：** 已读主实验与相关讨论，未审查全部附录或复现；预印本，交互方式分析不证明特定提示有效。

[论文 HTML](https://arxiv.org/html/2601.20245v1) · [研究机构解读](https://www.anthropic.com/research/AI-assistance-coding-skills)

<a id="r24"></a>

### R24 · Effective Personalized AI Tutors via LLM-Guided Reinforcement Learning

比较个性化与固定出题顺序的 AI 导师研究，配合 3.4 节。

**阅读范围：** 已读正文第 1—4.1 节相关内容；两组都有 AI，不能写成 AI 对比无 AI，发表与审稿状态未核实。

[作者提供的论文](https://hamsabastani.github.io/llmRL_doe.pdf)

<a id="r34"></a>

### R34 · OECD《AI 时代的技能》

OECD《AI 时代的技能》执行摘要，关注基础技能、批判思考、协作与 AI 素养。

**阅读范围：** 只读执行摘要；不是本指南六项技能的排名或成人学习效果验证。

[官方执行摘要](https://www.oecd.org/en/publications/skills-in-the-ai-age_972bd15e-en/full-report/component-4.html)

<a id="r39"></a>

### R39 · 有教学设计的 AI 导师：物理课交叉试验

Kestin 等（2025），AI tutoring outperforms in-class active learning，Scientific Reports 15：17458。用于 3.4 节，与独立掌握风险研究对照阅读。

**阅读范围：** 2026-10-18 已读结果、教学设计、研究对象、交叉设计与局限。特定课程的课后测验结果，不代表自由聊天、长期保持或替代教师。

[论文全文与 DOI](https://www.nature.com/articles/s41598-025-97652-6)

<a id="r41"></a>

### R41 · 一般学习方法：自测与分散练习

Dunlosky 等（2013），Improving Students’ Learning With Effective Learning Techniques，Psychological Science in the Public Interest。用于 3.5 节及 B.3 独立练习。

**阅读范围：** 2026-10-18 已读出版页完整摘要与方法评价结论，未逐项审阅全部原始实验。一般学习方法综述，不是生成式 AI 教学的直接效果证据。

[出版页与 DOI](https://journals.sagepub.com/doi/10.1177/1529100612453266)

<a id="d-4"></a>

## D.4 工作、求职与收入

<a id="r07"></a>

### R07 · 知识工作：对 AI 的信任与思考投入相关

知识工作者调查关注信任与自报思考投入，配合 2.3、3.4 节。

**阅读范围：** 只读机构摘要与书目信息；相关性不能证明 AI 导致智力下降。

[原始发布资料](https://www.microsoft.com/en-us/research/publication/the-impact-of-generative-ai-on-critical-thinking-self-reported-reductions-in-cognitive-effort-and-confidence-effects-from-a-survey-of-knowledge-workers/)

<a id="r08"></a>

### R08 · 就业：任务暴露不等于岗位消失

ILO 按任务分析职业暴露，适合理解 5.1 节的工作拆分。

**阅读范围：** 已读官方方法说明，完整报告未审查；潜在暴露不等于失业，也不用于计算个人风险。

[原始发布资料](https://www.ilo.org/publications/generative-ai-and-jobs-refined-global-index-occupational-exposure) · [补充入口](https://www.ilo.org/resource/article/how-might-generative-ai-impact-different-occupations)

<a id="r09"></a>

### R09 · 收入：效率收益未必很快变成工资变化

丹麦早期劳动市场研究，提醒省时与收入应分别验证，配合 5.3 节。

**阅读范围：** 只读原发布页摘要，未审查识别假设；限于国家和观察期，不预测全部长期收入。

[原始发布资料](https://www.nber.org/papers/w33777)

<a id="r15"></a>

### R15 · 求职：改善表达不等于编造经历

简历表达与招聘结果的写作辅助实验，配合 5.2 节。

**阅读范围：** 只读摘要；使用非生成式辅助，不能直接等同于聊天机器人或本地招聘效果。

[发布页](https://pubsonline.informs.org/doi/10.1287/mnsc.2024.04528)

<a id="r16"></a>

### R16 · 技能：岗位和地区有差异

OECD 同一技能报告的发布页，补充行业、地区与技能差异背景。

**阅读范围：** 只读发布页摘要；与 R34 同一报告的不同入口，不算两项独立效果证据。

[发布页](https://www.oecd.org/en/publications/skills-in-the-ai-age_972bd15e-en.html)

<a id="r17"></a>

### R17 · 自由职业：学会之后仍需展示能力

自由职业者学习与可信技能展示的困难，配合 5.2 节。

**阅读范围：** 只读预印本摘要；问卷与访谈不能证明某种作品集流程提高收入。

[发布页](https://arxiv.org/abs/2604.27231)

<a id="r23"></a>

### R23 · AI Skills Improve Job Prospects: Causal Evidence from a Hiring Experiment

招聘者评价虚构简历的实验调查，讨论 AI 技能信号，配合 5.2 节。

**阅读范围：** 只读预印本 v2 摘要；不是现实录用、工资或中国招聘市场实验。

[预印本摘要与版本记录](https://arxiv.org/abs/2601.13286v2)

<a id="d-5"></a>

## D.5 资料、发布、投入与家庭边界

<a id="r12"></a>

### R12 · 中国大陆：输入信息与使用记录的保护义务

中国大陆《生成式人工智能服务管理暂行办法》，第十一条涉及提供者的信息保护义务。

**阅读范围：** 已读第二、十一条；不表示用户可上传任何资料。现实使用另查当前法律、协议与单位要求。

[原始发布资料](https://www.cac.gov.cn/2023-07/13/c_1690898327029107.htm)

<a id="r13"></a>

### R13 · 中国大陆：发布生成内容时声明与标识

中国大陆《人工智能生成合成内容标识办法》正式文本，配合 6.3 节。

**阅读范围：** 已读相关条款与施行日期；平台具体流程未实测，实际发布另查当前要求。

[原始发布资料](https://www.cac.gov.cn/2025-03/14/c_1743654684782215.htm)

<a id="r14"></a>

### R14 · 赚钱案例：警惕 AI 被动收入保证

FTC 的 Click Profit 案通报，作为 AI 被动收入宣传的审阅案例。

**阅读范围：** 已读 2025 年通报，后续判决未核查；机构指控不是最终判决，不说明所有项目都相同。

[原始发布资料](https://www.ftc.gov/news-events/news/press-releases/2025/03/ftc-acts-stop-click-profit-online-business-opportunity-has-cost-consumers-least-14-million)

<a id="r18"></a>

### R18 · 迁移：数据导出不等于导入

数据导出与导入可能有不同限制，配合 3.5 节保存方法。

**阅读范围：** 已读 2026-10-11 的官方帮助，未实际迁移；产品功能变化时重新查当前说明。

[发布页](https://support.claude.com/en/articles/9450526-export-your-claude-data)

<a id="r19"></a>

### R19 · 家庭：仿冒熟人声音时独立核实

FTC 防骗指导建议使用已知号码回拨本人或另找亲友核实，配合 6.4 节。

**阅读范围：** 已读相关步骤；举报渠道属于美国背景，家庭演练由本项目设计。

[发布页](https://consumer.ftc.gov/articles/scammers-use-fake-emergencies-steal-your-money)

<a id="r20"></a>

### R20 · 儿童：安全、隐私和 AI 陪伴

UNICEF 儿童 AI 指导，关注安全、隐私与发展，配合 6.5 节。

**阅读范围：** 只读 3.0 版发布页与要求清单，未审查全书；不是亲子学习效果实验。

[发布页](https://www.unicef.org/innocenti/reports/policy-guidance-ai-children)

<a id="r21"></a>

### R21 · 情感互动：明确服务边界与退出

中国大陆拟人化互动服务正式规范，关注未成年人保护、现实提醒与退出。

**阅读范围：** 已读第二、十四、十八、十九条；限于所定义的持续性情感互动服务，不泛化到所有问答。

[发布页](https://www.cac.gov.cn/2026-04/10/c_1777558395078289.htm)

<a id="r36"></a>

### R36 · 外部资料中的提示注入

OWASP LLM01:2025 说明网页、文件等外部输入可能改变模型行为，并列出权限限制与关键操作确认等缓解办法。配合正文 6.2 阅读。

**阅读范围：** 2026-10-18 已读官方页面的定义、类型、缓解措施及示例；不是任何工具已完成安全认证的证明。

[官方说明](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)

<a id="d-6"></a>

## D.6 用户讲义的出处与使用范围

<a id="l01"></a>

### L01 · ENGG2112 第 10 周讲义

悉尼大学 ENGG2112 第 10 周讲义，Professor T. J. Lim，2026 Semester 2；用于模型、训练、RAG 与工具概念的原创解释。

**阅读范围：** 用户提供 47 页本地 PDF，已提取全文并检查缩略图与关键页面；未核查全部推导，没有公开入口，不分发原文件。
