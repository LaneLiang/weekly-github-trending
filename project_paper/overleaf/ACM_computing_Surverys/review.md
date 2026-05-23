27-Jan-2026



Dear Prof. Zhang:



I write you in regards to manuscript # TPEL-RegAP-2025-12-4301 entitled "Deep Reinforcement Learning for Power Electronic Converters: A Comprehensive Review of Design, Control, and Maintenance" which you submitted to the IEEE Transactions on Power Electronics.



In view of the feedback of the reviewer(s) found at the bottom of this letter, your manuscript has been rejected for publication in IEEE Transactions on Power Electronics.



Thank you for considering IEEE Transactions on Power Electronics for the publication of your research. I hope the outcome of this specific submission will not overly discourage you. As our journal's popularity has increased we are no longer able to publish the substantial majority of the submissions we receive. We ask you not to submit revisions or resubmissions of this paper to our journal; it is likely any resubmissions will receive the same decision and only delay your paper's successful publication elsewhere.



Sincerely,



Dr. Xiongfei Wang

Editor in Chief, IEEE Transactions on Power Electronics

xiongfei@tsinghua.edu.cn



Co-EIC: 1

Comments to the Author (Required):

Reviwers and AE brought up many concerns mainly related to the quality of the review.



Associate Editor: 2

Comments to the Author (Required):

Dear Authors,

A good overview should be both highly accurate and carefully select the papers presented to the reader. Unfortunately, this is not the case for your paper, among other critiques.



Reviewer Responses:



Reviewer: 1



Comments:

Comments to authors:

1\. The introduction and contribution list emphasize completeness and lifecycle coverage in section-I but do not clearly distinguish the manuscript’s analytical novelty from existing DRL review papers. Please explicitly state what new analytical insight, taxonomy, or unifying framework this paper provides beyond broader literature aggregation.

2\. The publication trend figures are informative but largely descriptive. Consider extracting deeper insights, such as shifts in algorithm preference, application maturity, or hardware validation trends over time.

3\. Algorithms such as DDPG, PPO, TD3, SAC, and multi-agent variants are described individually in section-II, but there is no structured comparative analysis across performance, stability, or implementation dimensions.

4\. The review cites and critically discusses a substantial number of conference papers. While conference publications are valuable for tracking early developments, IEEE Transactions on Power Electronics typically emphasizes mature, archival journal contributions. The authors are encouraged to clearly distinguish conference-level proof-of-concept studies from journal-level validated works and, where possible, prioritize extended journal versions when drawing conclusions about performance, robustness, and practical readiness.

5\. Stability and safety are mentioned but not treated with sufficient rigor for TPEL, especially given the safety-critical nature of power electronic converters.

6\. Covering design, control, and maintenance in one article is ambitious. Please clarify the intended depth of analysis in each domain and explicitly acknowledge any limitations arising from the broad scope.

7\. The conclusion identifies open challenges but remains high-level. Please improve future research directions with more concrete and technically actionable guidance.

8\. It is important to cite the recent review papers on the DRL for power electronics.







Reviewer: 2



Comments:

This paper presents a comprehensive review of artificial intelligence (AI), particularly reinforcement learning (RL), applications in the control of power electronic converters. The topic is timely and important. Nevertheless, key findings could be further synthesized. The following comments are provided for improvement:

1\. More state-of-the-art references should be cited as current literature is mostly from year 2022-2024. Considering the growing interest in RL applications in converters, more recent studies should be cited and reviewed.

2\. The identified gap regarding the unified review of RL applications in the life cycle of the power converter could be more comprehensive. It would be beneficial to provide a brief review of the synthesis of these problems throughout the life cycle of power converters. How to connect them within a unified framework is the key.

3\. Reviewing the applications of RL algorithms in PECs over the years is strange. What is the point of this section? In addition, those applications will also be reflected in the following categories.

4\. For a given RL approach, it would be valuable to explore its unique functions in different, distinct problem areas. Additionally, an examination of the tailored solutions it offers for the key characteristics of each problem would provide greater clarity. I recommend strengthening the synthesis of these types of problems and incorporating more summary diagrams. Such visual aids would not only enhance the overall readability but also facilitate a more intuitive understanding of the complex relationships involved.

5\. For the control section, what is the current strategy of applying RL in power converter control? Considering most studies are dedicated to control, it is suggested to provide a summary diagram first and then provide detailed reviews. This could help readers to grasp the typical ways of employing RL for converter control. Again, more state-of-the-art literature should be reviewed. In addition, it is difficult to follow the current organization of this section. Please organize those content in a clearer way.

6\. For maintenance, an important topic regarding RL in cyberattack or fault area of PECs is not reviewed. In addition, the reviewed studies do not exactly correspond to the assigned category. The condition monitoring and RUL prediction have overlapped. Please improve this subsection significantly.

7\. There are relevant studies that focused on the safety and stability of RL in power converters, while the cited references are from voltage control rather than power converter control. Please cite correct and relevant studies.

8\. Computational efficiency should be discussed from two perspectives. The offline stage and the online stage.

9\. Although RL has demonstrated its effectiveness in alleviating certain issues, when considering the combination of power electronic converters, reinforcement learning, and the broader realm of AI, there remains a significant need for breakthroughs in the fundamental theoretical analysis of power electronic converters. Currently, reinforcement learning and other AI methods often address specific problems rather than offering universal solutions. Further progress in the underlying theories and concepts would be crucial for advancing this field.

10\. The discussion and future studies could be more in-depth by providing potential solutions, which could be adopted from current development in other domains or similar.







Reviewer: 3



Comments:

The authors present the state of the art of DRL and its applications in power electronics. The overview is detailed, and it critically assesses the methods. I have the following recommendations for the authors.



1\) Can you also include a discussion on the position of the DRL within the other AI-based methods? In which you can highlight advantages and disadvantages, for readers, it would be useful to know what can be done better if DRL is used, but also what the cost is. For power electronics engineers, it is of value to correctly select the AI-methods for their problem.



2\) Are most of the DRL applications in academia, or are there any industrial applications already published? It might be relevant to address what is still hindering the transition to field applications, both from the side of algorithm development and practical issues related to power electronics applications. Could be something for the outlook.



3\) Section III is missing references to the studies on which the authors base their conclusions. There are some references in the table afterwards, but it would be appropriate to also provide examples in the text.



4\) DRL is usually heavier on computational burden than other AI based method - maybe reflecting on that part would be beneficial i.e., what computational resources are needed for running those algorithms.



4\) The manuscript is heavy on the text; maybe some more concepts could be illustrated? For example, it could also be a concept figure that shows what the requirements are for each task (design, control etc.) and which method is suitable.







Reviewer: 4



Comments:

This paper reviews papers on deep reinforcement learning for power electronics converters, in terms of design, control and maintenance.



First of all, since this is a kind of the review paper, investigation and organization of papers are very important. However, this paper loses this important thing because there are many wrong papers and low quality papers. It must be improved a lot.



1\. Wrong literature review of papers. There are so many wrong classifications of papers in Fig. 5.

In Fig. 5, \[75] is in Q-learning group, but this paper used DQN as the RL agent. \[49] used DDQN, but this manuscript defines it as DQN relevant paper. \[51] and \[64] used DQN, but they are classified as DDQN… \[88] is defined as the paper using DDPG in this manuscript, but actually this paper used TD3. Regarding A3C paper, \[56] is introduced, but it is about MADDPG… This manuscript introduced 3 papers about SAC RL agent, but two of them are not related to SAC, \[97] is about DDPG and \[103] is about Q-learning… In Table II, \[116] is categorized as TD3, but it is introduced as the paper using PPO in Table IX.

Even though I selected some papers randomly, almost half of them are wrong match of RL methods…



2\. Section III described RL methods according to the time line. However it is not convincing at all. Regarding ‘Section III.A – Value-based Learning (2015-2017)’, there is only one paper within this period (2015-2017) in Fig. 5 and Table II, but most of them are published between 2020-2023. “During the early stage, DRL research in PECs primarily employed value-based algorithms such as Q-learning, DQN, and DDQN.” What does it mean?? There are few papers using Q-learning or Q-Network for PECs in 2015-2017

Similarly, ‘Section III.B Policy-Gradient Optimization (2017-2019)’, most of the paper related to PG, DDPG and even TD3 are published between 2020-2023.



3\. Many cited papers were presented at conferences and their quality is not good enough. It doesn’t indicate clear contribution of RL to PEC. Please review enough quality papers.



4\. In Section VII, Limitations and Future Opportunities are discussed. As a review paper, it is very important to show the perspective of authors. However, most of them are too vague. For example, in Table X, ‘Limitation – Limted interpretability’ why do authors think SHAP/LIME can be a solution?? What is SHAP/LIME? It is known as classification of static images?  What context is this about using ‘Federated learning’ to protect privacy when central control is difficult? Section VII is pointless

