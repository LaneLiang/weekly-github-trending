# Reading Notes: Red/Yellow Batch 1

These notes trace the five highest-risk preferred-core papers that could cause algorithm-classification errors in Paper A. Full PDFs were not available through the current non-browser session, so each note distinguishes verified evidence from unresolved items.

## 1. `hajihosseini2020dc`

**Full citation:** Mojtaba Hajihosseini, Milad Andalibi, Meysam Gheisarnejad, Hamed Farsizadeh, and Mohammad-Hassan Khooban, "DC/DC Power Converter Control-Based Deep Machine Learning Techniques: Real-Time Implementation," IEEE Transactions on Power Electronics, 35(10), 9971-9977, 2020. DOI: `10.1109/TPEL.2020.2977765`.

**Access route checked:** Crossref resolved DOI to IEEE document `9020169`. Direct IEEE PDF download through `stamp.jsp` failed in the current session with HTTP 418. Deakin repository metadata page was discoverable but not fetchable by the web tool due to 403.

**What is verified:** The article is in TPE, therefore it matches the preferred-core venue rule. Crossref confirms title, venue, pages, year, and DOI. Search metadata from Deakin identifies keywords including DC-DC buck-boost converter and deep reinforcement learning.

**Likely method role:** The title says "deep machine learning techniques," not explicitly DRL. Existing metadata suggests DRL is involved, but the exact algorithm family is not confirmed from a method section in this session.

**Experiment/validation evidence:** The title claims real-time implementation, but exact platform, hardware, and experiment design require PDF or IEEE full page access.

**Paper A decision:** Conditional keep. It may support "real-time machine-learning control for DC/DC converters" after source PDF verification, but it must not be placed in a DDPG/PPO/SAC/DQN class until the method section is checked.

**Unresolved before use in figures:** exact algorithm, controller architecture, converter type, hardware platform, and whether results are experimental or HIL.

## 2. `meng2022novel`

**Full citation:** Xiangqi Meng, Yanbing Jia, Qianwen Xu, Chunguang Ren, Xiaoqing Han, and Peng Wang, "A Novel Intelligent Nonlinear Controller for Dual Active Bridge Converter With Constant Power Loads," IEEE Transactions on Industrial Electronics, 70(3), 2887-2896, 2023. DOI: `10.1109/TIE.2022.3170608`.

**Access route checked:** Crossref resolved DOI to IEEE document `9767707`. Direct IEEE PDF download failed with HTTP 418. KTH DiVA/SwePub metadata pages are accessible.

**What is verified:** KTH/SwePub abstract states that the paper proposes a deep-reinforcement-learning-based backstepping control strategy for DAB converters feeding CPLs. It uses a nonlinear disturbance observer, a backstepping controller, and a DRL-based compensation method. KTH keywords identify "twin-delayed deep deterministic policy gradient."

**Likely method role:** Hybrid nonlinear control. DRL is not the sole controller; it acts as an intelligent compensation/adaptation layer around disturbance-observer/backstepping control. The likely algorithm is TD3, but the exact implementation details should be confirmed from the PDF.

**Experiment/validation evidence:** KTH/SwePub abstract states effectiveness is verified by experiments.

**Paper A decision:** Keep as preferred-core DAB evidence. Classify under "hybrid nonlinear control / DRL compensation," not under direct policy control. Do not count it as generic DDPG unless PDF confirms the algorithm.

**Unresolved before use in figures:** exact TD3 formulation, state/action/reward definitions, experimental setup, and whether the DRL component runs online or is trained offline.

## 3. `fathollahi2023robust`

**Full citation:** Arman Fathollahidehkordi, Meysam Gheisarnejad Chirani, Bjorn Andresen, Hamed Farsizadeh, and Mohammad Hassan Khooban, "Robust Artificial Intelligence Controller for Stabilization of Full-Bridge Converters Feeding Constant Power Loads," IEEE Transactions on Circuits and Systems II: Express Briefs, 70(9), 3504-3508, 2023. DOI: `10.1109/TCSII.2023.3270751`.

**Access route checked:** Crossref resolved DOI to IEEE document `10109206`. Direct IEEE PDF download failed with HTTP 418. Aarhus Pure metadata page is accessible but does not provide the full abstract. A secondary Power Electronics News page summarizes the method.

**What is verified:** The paper is in TCAS-II and therefore matches preferred-core venue rules. Aarhus Pure confirms title, authors, venue, pages, DOI, and lists fingerprints including reinforcement learning and deep neural network.

**Likely method role:** Robust nonlinear control for full-bridge converters feeding CPLs. Secondary summary states the method uses deep reinforcement learning and identifies SAC for tuning controller parameters; this must be verified from the source paper before final classification.

**Experiment/validation evidence:** Not sufficiently verified in this session. The source PDF is required to determine whether validation is simulation, HIL, or experimental.

**Paper A decision:** Conditional keep. It is relevant to stabilization of full-bridge converters, but algorithm label and validation maturity remain unresolved. Do not use it in algorithm-count figures yet.

**Unresolved before use in figures:** SAC confirmation, control law, state/action/reward, validation platform, comparison baselines, and hardware evidence.

## 4. `gheisarnejad2022reducing`

**Full citation:** Meysam Gheisarnejad Chirani, Allahyar Akhbari, Mohsen Rahimi, Bjorn Andresen, and Mohammad Hassan Khooban, "Reducing Impact of Constant Power Loads on DC Energy Systems by Artificial Intelligence," IEEE Transactions on Circuits and Systems II: Express Briefs, 69(12), 4974-4978, 2022. DOI: `10.1109/TCSII.2022.3194271`.

**Access route checked:** Crossref resolved DOI to IEEE document `9843888`. Direct IEEE PDF download failed with HTTP 418. Aarhus Pure metadata page is accessible and includes abstract and keywords.

**What is verified:** Aarhus Pure abstract states that the paper proposes a robust control technique based on DRL to stabilize a DC microgrid with parallel boost converters feeding CPLs. It applies a model-free sliding mode controller (MFSMC). Key coefficients are designed by PPO RL with actor and critic neural networks. Validation uses an OPAL-RT setup through HIL simulations.

**Method role:** Hybrid control. PPO tunes MFSMC coefficients rather than directly outputting converter switching actions. This should be classified as "hybrid parameter tuning / safety-stability control," not direct control.

**Experiment/validation evidence:** OPAL-RT HIL simulation is verified from the Aarhus abstract.

**Paper A decision:** Keep. This is strong evidence for PPO-assisted robust control and HIL validation in a DC microgrid with parallel boost converters.

**Unresolved before final prose:** PDF should still be checked for exact state/action/reward and comparison baselines, but the high-level classification is sufficiently supported for the evidence table.

## 5. `khooban2022smartenance`

**Full citation:** Mohammad Hassan Khooban, "Smartenance DC-DC On-Board Power Converters," IEEE Transactions on Circuits and Systems II: Express Briefs, 70(1), 191-195, 2023. DOI: `10.1109/TCSII.2022.3206230`.

**Access route checked:** Crossref resolved DOI to IEEE document `9888784`. Direct IEEE PDF download failed with HTTP 418. Aarhus Pure metadata page is accessible and includes abstract and keywords.

**What is verified:** Aarhus Pure abstract states that the study develops a non-integer MPC for DC/DC converters with CPLs to stabilize bus voltage and current in a full-electric ferry ship. It applies DDPG with actor and critic neural networks to design coefficients embedded in the non-integer MPC. Keywords include DC/DC converter control, stabilization of DC ferry ships, DRL, and non-integer MPC.

**Method role:** Hybrid MPC parameter design/tuning. DDPG tunes coefficients in a non-integer MPC; it should not be classified as direct DDPG converter control.

**Experiment/validation evidence:** Aarhus abstract says experimental results with comparative analysis are carried out, but exact hardware/platform details require PDF confirmation.

**Paper A decision:** Reclassify from "maintenance" to Paper A hybrid control if used. The title "Smartenance" is misleading for our taxonomy; the abstract is about DRL-assisted controller design for onboard DC/DC converters, not PHM maintenance. Keep only under hybrid MPC/embedded maritime DC microgrid control after PDF validation.

**Unresolved before final prose:** exact experiment platform, online/offline training split, action variables, and whether deployment constraints are discussed.

## Batch-Level Conclusions

1. `gheisarnejad2022reducing` is no longer a red/yellow item for high-level classification: it is PPO-assisted MFSMC with OPAL-RT HIL evidence.
2. `khooban2022smartenance` should be rescued for Paper A as hybrid DDPG-MPC control, not moved automatically to Paper C.
3. `meng2022novel` is a strong Paper A candidate, but it should be classified as DRL-assisted nonlinear/backstepping compensation, likely TD3, not generic DRL.
4. `fathollahi2023robust` remains yellow because method and validation details are not sufficiently verified from an official abstract in this session.
5. `hajihosseini2020dc` remains yellow because "deep machine learning" is too broad; despite DRL keywords in metadata, the exact method requires PDF/source verification.

## Network Verification Update

After switching from SEU full-text retrieval to web-verifiable evidence, the batch status is updated as follows:

| Key | Updated status | Classification rule |
|---|---|---|
| `hajihosseini2020dc` | Verified-source-limited | Aarhus Pure abstract supports actor-critic DRL with ULM feedback gain adaptation and dSPACE MicroLabBox real-time testbed. It must not be counted as DDPG/PPO/SAC/TD3/DQN because the accessible source does not name such a subalgorithm. |
| `meng2022novel` | Verified-source | KTH DiVA abstract/keywords support TD3-assisted DRL compensation with nonlinear disturbance observer/backstepping control and experimental validation. Count as TD3 only under hybrid compensation. |
| `fathollahi2023robust` | Secondary-confirmed / conditional | Secondary technical reporting supports SAC and HIL/real-time validation, but accessible institutional metadata does not expose method/experiment detail. Do not count in SAC figures. |
| `gheisarnejad2022reducing` | Verified-source | Aarhus Pure abstract supports PPO actor-critic tuning of MFSMC coefficients and OPAL-RT HIL validation. Count as PPO-assisted hybrid robust-control tuning. |
| `khooban2022smartenance` | Verified-source | Aarhus Pure abstract supports DDPG actor-critic coefficient design embedded in non-integer MPC and experimental comparative results. Count as DDPG-assisted MPC parameter design, not maintenance. |

The detailed tabular record is now maintained in `classification_table_red_yellow_batch1.md` and `classification_table_red_yellow_batch1.csv`.

## Source Reliability Notes

- Highest reliability in this batch: Aarhus Pure pages with abstract and DOI for `gheisarnejad2022reducing` and `khooban2022smartenance`; KTH/SwePub page for `meng2022novel`.
- Medium reliability: Aarhus Pure metadata without abstract for `fathollahi2023robust`.
- Lower reliability: search-result metadata for `hajihosseini2020dc`, pending source PDF.
