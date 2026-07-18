# driftline

[中文](#中文) · [English](#english)

## 中文

**没有一条固定的基准线，漂移就无法被看见。**

每隔几个月，Hacker News 都会重复同一场争论：*模型变差了。他们削弱了模型。他们在故意消耗我的 token。* 2023 年的相关讨论获得了 [309 points](https://news.ycombinator.com/item?id=36815594)，[反驳文章](https://www.aisnakeoil.com/p/is-gpt-4-getting-worse-over-time)也获得了 149。三年后，人们仍在争论，却依然只有感受，没有记录。

这个仓库负责留下记录：相同任务、相同评分器、相同提示词，按固定周期持续运行。每一条原始回答都提交到 git，因此你可以完全抛开我们的评分方式，用自己的方法重新分析。

它是一件测量仪器，不是一份指控。如果模型没有变化，这个仓库也会用同样清楚的声音报告这一结果。

![10 个模型的行为与能力对比，基线日期 2026-07-16](assets/baseline_2026-07-16.svg)

两根柱子之间的差距既是发现，也是陷阱。简短询问 gpt-5.4 或 deepseek-v4-flash 时，它们的表现约为 60–65%；允许它们推理后，可测得的能力约为 97–98%。如果沿用 2023 年论文的评分方法——只给简短提示词、只测试质数——模型看起来像是坏掉了，但实际并非如此。**这只是基线，不是漂移结论**；单个时间点无法证明漂移。详见 [RESULTS.md](RESULTS.md)。

---

### 这件仪器首先检查自己

2023 年研究的实验设计无法清楚地区分能力下降与两种特定的行为和格式变化。这不代表它当年的观察一定错误，而是说明那些测试无法单独确认“GPT-4 变差了”这一标题式结论。在测量任何模型之前，这套基准必须先证明自己没有重复同样的混淆因素。

`scripts/demo_2023_replay.py` 会构造一个真实能力被**固定在代码里**的合成模型——它在设计上不可能变笨——然后只改变模型面对简短提示词时的回答先验，这正是微调可能带来的普通变化。脚本随后用两种方法为同一个模型评分：

```text
THE 2023 METHOD  (prime-only task set, raw accuracy)
  before:  94.2%
  after:    9.7%
  headline it would produce: 'accuracy collapsed by 84 points'

DRIFTLINE  (balanced task set, behavior vs capability split)
  behavior            92.2%  ->   53.9%
  capability         100.0%  ->  100.0%
  recall_positive     93.3%  ->    8.9%     <- all 2023 looked at
  recall_negative     91.1%  ->   98.9%     <- what it never looked at
  answer_bias(yes)    51.1%  ->    5.0%     <- the actual cause

  VERDICT: BEHAVIOR DRIFT: accuracy on the canonical prompt declined, but
  capability held under rephrasing. The model can still do the task; it
  stopped doing it when asked the usual way. This is NOT evidence of
  degradation.
```

这个合成示例中的模型从未改变。它不是在重新裁决论文当年的真实实验，而是在证明一个更窄的结论：即使真实能力保持不变，同一种评估设计仍然可能报告 84 个百分点的能力崩塌。可以运行 `python3 scripts/demo_2023_replay.py` 自行复现。

### 两个混淆因素，以及由此产生的规则

**1. 质数陷阱。** 2023 年论文连续 500 次询问“X 是质数吗？”，而 500 个数字全部都是质数。如果模型的回答倾向逐渐偏向“否”，测试就可能把这种变化误判为能力丧失。上面的示例展示了这一失败模式：`recall_positive` 从 93 降到 9，`recall_negative` 却从 91 上升到 99。只包含质数的任务集无法观察向另一个方向变化的那一半。

→ 始终平衡正负类别。使用**平衡准确率**，而不是原始准确率。模型的**回答偏差**是一项一级指标，因为先验变化本身是真实发现，只是它与“模型变笨了”完全不是一回事。

**2. Markdown 陷阱。** 2023 年论文检查生成的代码能否被*直接执行*。GPT-4 开始用代码围栏包装答案以提升可读性，但围栏会破坏直接执行，从而把格式变化误判成编程能力崩塌。

→ 评分器先提取答案，再判断其**语义**。代码会从围栏中提取出来，通过单元测试执行，并按正确性评分。格式作为独立指标记录，绝不与能力混在一起。

**3. 行为 ≠ 能力。** 如果一种能力在某个问法下隐藏、换个问法又出现，那么发生的是漂移，而不一定是退化。

→ 始终同时发布两个核心数字。`behavior` 代表用户实际输入的标准提示词；`capability` 代表固定改写提示词集合上的 best-of-N。只有两者同时下降，才可以称为退化。

### 专门为测量漂移而制定的规则

- **永远不使用 LLM Judge。** Judge 本身也会漂移；用一把会漂移的尺子测量漂移，会让结果无法归因。所有评分器都是带单元测试的确定性代码。无法用这种方式评分的任务不会进入基准——不测文章质量，也不测“有帮助程度”。一套范围较窄但可归因的基准，比范围广却无法归因的基准更有价值。
- **原始回答才是产物，分数只是派生观点。** 克隆仓库、删除我们的评分器、写一套你自己的，然后重新计算三年的历史数据。这正是保存原始数据的目的。2023 年的争论之所以变成所有人互相抛先验，是因为没有人能够重新运行别人的评分。
- **零结果也要以同样醒目的方式发布。** 如果一个基准只有在找到“反派”时才值得报道，那它只是带图表的倡议活动。
- **采样噪声不是漂移。** 每个提示词采样 k 次，使用 bootstrap 95% 置信区间；除非区间彼此分离，否则不把变化称为漂移。

完整的预注册方法，以及**目前已经知道的设计缺陷**，见 [METHODOLOGY.md](METHODOLOGY.md)。

### 当前状态

首个基线已于 **2026-07-16** 收集，覆盖 **10 个模型**。结果见 [RESULTS.md](RESULTS.md)，图表位于 `assets/`。本次包含 30 个质数判断任务（平衡、固定随机种子、冻结）、一个执行代码评分器，以及 k≥2 层级的 bootstrap 置信区间。

目前仍然只有一个时间点，因此还不能提出漂移结论；至少需要第二次运行。请阅读 METHODOLOGY.md 的 “Known defects” 章节了解真实限制，其中包括：前沿模型层级仍为 k=1；由于上游服务中断，本次开放权重一侧只覆盖了 DeepSeek。

### 利益冲突

这个仓库主要由 Claude（Anthropic）在仓库所有者的指导下编写，而 Anthropic 正是本基准所测量的供应商之一。这是真实存在的利益冲突，任何口头保证都无法消除它。

缓解方式只能来自结构：方法在数据收集前预注册；评分器是确定性的，并带有单元测试；每一条原始回答都会进入 git。任何不信任作者身份的人，都可以在不需要我们配合的情况下重新计算全部历史结果。

请真的这样做。

### 运行

```bash
python3 -m pytest tests/ -q          # 21 项测试，包括两个 2023 失败模式的回归测试
python3 scripts/gen_primality.py     # 重新生成冻结任务集（固定种子、字节完全一致）
python3 scripts/demo_2023_replay.py  # 运行上面的自检
```

### 许可

MIT。

---

## English

**Drift is invisible until you have a fixed line to measure it against.**

Every few months, Hacker News has the same argument: *the model got worse. They
nerfed it. They're burning my tokens on purpose.* In 2023 the argument ran to
[309 points](https://news.ycombinator.com/item?id=36815594); the
[rebuttal](https://www.aisnakeoil.com/p/is-gpt-4-getting-worse-over-time) ran to
149. Three years later people are still having it, still with nothing but vibes,
because nobody kept a record.

This repo keeps the record. Same tasks, same graders, same prompts, run on a
schedule, forever. Every raw response committed to git so you can throw out our
scoring and do your own.

It is a measuring instrument, not an accusation. If the models are fine, this
repo will say so, at exactly the same volume.

![behavior vs capability across 10 models, baseline 2026-07-16](assets/baseline_2026-07-16.svg)

The gap between the two bars is the finding — and the trap. Ask gpt-5.4 or
deepseek-v4-flash tersely and they read ~60–65%; let them reason and they're
~97–98% capable. Score them the way the 2023 paper did (terse prompt, primes
only) and they look broken. They aren't. **This is a baseline, not a drift
claim** — one time point cannot show drift. See [RESULTS.md](RESULTS.md).

---

### The instrument checks itself first

The 2023 study's design could not cleanly distinguish capability loss from two
specific behavior and formatting changes. That does not prove its historical
observations were false; it means the headline conclusion — *GPT-4 got worse* —
was not identified by those tests. Before this benchmark measures anyone, it has
to prove it doesn't repeat those confounds.

`scripts/demo_2023_replay.py` builds a synthetic model whose true competence is
**fixed in code** — by construction it cannot get dumber — and shifts only its
answer prior on terse prompts, the most boring thing fine-tuning does. Then it
scores that model both ways:

```
THE 2023 METHOD  (prime-only task set, raw accuracy)
  before:  94.2%
  after:    9.7%
  headline it would produce: 'accuracy collapsed by 84 points'

DRIFTLINE  (balanced task set, behavior vs capability split)
  behavior            92.2%  ->   53.9%
  capability         100.0%  ->  100.0%
  recall_positive     93.3%  ->    8.9%     <- all 2023 looked at
  recall_negative     91.1%  ->   98.9%     <- what it never looked at
  answer_bias(yes)    51.1%  ->    5.0%     <- the actual cause

  VERDICT: BEHAVIOR DRIFT: accuracy on the canonical prompt declined, but
  capability held under rephrasing. The model can still do the task; it
  stopped doing it when asked the usual way. This is NOT evidence of
  degradation.
```

The model in this synthetic example never changed. This does not re-litigate the
paper's exact historical runs; it demonstrates the narrower point that the same
evaluation design can report an 84-point capability collapse even when capability
is fixed. Run it yourself: `python3 scripts/demo_2023_replay.py`.

### The two confounds, and the rules they produced

**1. The prime trap.** The 2023 paper asked "Is X prime?" 500 times. All 500 numbers
were prime. A model drifting toward "no" could therefore look like it had lost the
capability — you can see the failure mode above: `recall_positive` cratered 93→9
while `recall_negative` *rose* 91→99. A prime-only task set cannot observe the half
moving in the other direction.

→ Balanced positive/negative classes, always. **Balanced accuracy**, never raw. The
model's **answer bias** is a first-class metric, because a prior shift is a real
finding — just a completely different one from "it got dumber."

**2. The markdown trap.** The 2023 paper checked whether generated code was *directly
executable*. GPT-4 had started wrapping code in fences to be helpful; the fences broke
execution and could turn a formatting change into an apparent coding collapse.

→ Graders extract the answer, then judge its **semantics**. Code is pulled out of
fences, executed against unit tests, judged on correctness. Formatting is tracked as
its own metric and never mixed into capability.

**3. Behavior ≠ capability.** A capability that hides behind one phrasing and appears
behind another has drifted, not degraded.

→ Two headline numbers, always shipped together. `behavior` = the canonical prompt
you actually type. `capability` = best-of-N over frozen paraphrases. Only both
falling together may be called degradation.

### Rules that exist because this measures drift specifically

- **No LLM judges. Ever.** A judge drifts too; grading drift with a drifting ruler
  makes the result unattributable. Every grader is deterministic code with unit
  tests. Tasks that can't be graded that way don't go in — no essay quality, no
  "helpfulness." A narrower benchmark that is attributable beats a broad one that
  isn't.
- **Raw responses are the artifact; scores are a derived opinion.** Clone the repo,
  delete our graders, write your own, re-score three years of history. That's the
  point. The 2023 fight became people shouting priors because nobody could re-run
  anyone's scoring.
- **Null results ship just as loudly.** A benchmark that's only newsworthy when it
  finds a villain is advocacy with a chart on it.
- **Sampling noise is not drift.** k samples per prompt, bootstrapped 95% CIs,
  nothing called a change unless the intervals separate.

Full pre-registered method, including **the defects we already know about**:
[METHODOLOGY.md](METHODOLOGY.md).

### Status

First baseline collected: **10 models, 2026-07-16** — see [RESULTS.md](RESULTS.md)
and the chart in `assets/`. 30 primality tasks (balanced, seeded, frozen), an
executed-code grader, bootstrap CIs on the k≥2 tier. Still one time point, so no
drift claims yet — that needs a second run. See METHODOLOGY.md § "Known defects" for
what's honestly limited (notably: the frontier tier is k=1, and coverage this run is
deepseek-only on the open-weight side due to upstream outages).

### Conflict of interest

This repo was largely written by Claude (Anthropic), at the direction of the repo
owner. Anthropic is one of the vendors this benchmark measures. That is a real
conflict and no promise from us fixes it. The mitigations are structural instead:
the method is pre-registered before data collection, the graders are deterministic
and unit-tested, and every raw response lands in git so anyone who distrusts the
authorship can re-score the entire history without our cooperation.

Please do.

### Run it

```bash
python3 -m pytest tests/ -q          # 21 tests, incl. regressions against both 2023 failure modes
python3 scripts/gen_primality.py     # regenerate the frozen task set (seeded, byte-identical)
python3 scripts/demo_2023_replay.py  # the self-check above
```

### License

MIT.
