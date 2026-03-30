# Stage 1 Milestone

## Goal

第一阶段的目标不是实现完整方法，也不是接通真实仿真器，而是将项目从“想法 + 文档”推进到“可执行的研究平台雏形”。阶段一完成后，项目应具备明确且冻结的问题定义、稳定的配置入口、结构化数据契约以及最小可运行的样本生成流水线。

## Completion Criteria

第一，仓库顶层结构已经固定，包括 README、configs、docs、scripts、src、data、results 和 tests 等目录，并与论文叙事保持一致。第二，核心文档初稿已经完成，包括 proposal、methodology、simulation_pipeline、data_schema、experiment_protocol，以及 failure mode、uncertainty validation、hard case、wall-clock 和 paper figures 等扩展文档。第三，主实验配置文件已经形成，能够明确随机种子、初始采样大小、预算和评价指标。第四，固定研究对象已冻结为两级运放，并拥有独立的设计空间配置文件。第五，样本 schema 已从文档上升为程序契约，定义了设计变量、性能指标、可行性、约束状态、边界语义、仿真状态和来源阶段等关键字段。第六，最小流水线已跑通，即能够生成初始设计、构造样本并输出结构化数据文件，即使当前仿真器仍为 mock 版本。

## Deliverables

阶段一结束时，至少应存在以下实际产物：一份可执行的 `configs/experiment/exp_main.yaml`；一份固定对象的 `configs/circuit/opamp.yaml`；一个最小版 `src/data/schema.py`；一个临时 `src/simulation/mock_simulator.py`；可运行的 `scripts/generate_initial_designs.py` 与 `scripts/build_dataset.py`；以及一份示例数据文件 `data/processed/dataset_v0.json`。

## Out of Scope

以下内容不属于第一阶段完成标准：真实 Spectre 仿真接入、代理模型训练结果、failure mode 定量图、不确定性校准结果、完整优化闭环和 baseline 对比实验。这些属于后续阶段内容，不应在第一阶段过度展开。