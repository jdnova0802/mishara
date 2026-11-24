# Phase 3 — Perception / Control (home curriculum)

Checkpoint format, same rigor as Phase 1 (artificial-intelligence / adversarial-machine-learning security with signal-detection-theory scoring) and Phase 2 (hybrid Module-Lattice-Based Key-Encapsulation Mechanism (ML-KEM) + Transport Layer Security (TLS) crypto). This is the Deep physical subject: estimation and control for autonomous stacks. It is **not** mechanical/aerospace shop work.

**Cadence:** about **30 hours/week**, Thursday–Saturday only. Sunday–Wednesday warehouse overnight: **no study**. Do not split a milestone across a week unless the Do-list says so.

**Constraints:** zero capital beyond a laptop; home-executable; no clearance; **spoken-recall checkpoints only** (no notebook/tracker/written logging system as the *proof*). You may keep code. You may not substitute a written journal for the spoken gate.

**URL check:** every link below returned **HTTP 200** or a **named redirect** on **24 November 2026, America/New_York**. Dead or 403/404 links were dropped, not invented.

**Simulation honesty:** everything here is **software-in-the-loop (SITL)** or **offline datasets**. A hover in jMAVSim is **not** a hardware-validated flight. Say that out loud at the portfolio gate.

---

## Where this slots (Phase 1 → Phase 2 → Phase 3)

**Sequential: start Phase 3 only after Phase 2’s home 10/10 exit gate.** Same “finish the gate before starting the next” rule as Phase 1 → Phase 2.

Not because Kalman needs Kyber. It does not. ML-KEM and TLS do not appear in this file.

**Reason:** the bottleneck is **hours**, not domain. Thirty hours Thursday–Saturday cannot carry two Deeps. “They are different subjects so run them in parallel” is how both stay unfinished. Phase 1 then Phase 2 is the **Gate-now / hiring** order. Phase 3 is the **later physical-autonomy company**. Starting it early does not buy a 2026 software seat.

**Do not wait** on a Phase 2 *upstream merge* or a lab you do not have. Wait on **Phase 2’s home 10/10** (local ML-KEM + hybrid handshake work as that curriculum defined it).

**The only intellectual borrow from Phase 1:** signal detection theory (SDT) is **detection** (is this H1?). Kalman is **estimation** (where is x?). Same probability objects; different question. One spoken line in M4. Do not restudy receiver-operating-characteristic (ROC) curves under a robotics sticker.

---

## Spine (what this is)

- Linear / extended / unscented Kalman filters (KF / EKF / UKF)
- Simultaneous localization and mapping (SLAM) and visual-inertial odometry (VIO) as **estimation**, not as a gazebo tour
- Model predictive control (MPC)
- Estimation under uncertainty: process noise, measurement noise, consistency (normalized estimation error squared (NEES), normalized innovation squared (NIS))

**Tooling (anchors, like Ollama/garak/PyRIT in Phase 1 and mlkem-native/OpenSSL in Phase 2):**

- NumPy / SciPy / Matplotlib for filters written by you
- Robot Operating System 2 (ROS 2) **Humble**
- PX4 Autopilot **SITL**, default **jMAVSim** (lighter than Gazebo)
- EuRoC micro aerial vehicle (MAV) dataset + OpenVINS
- KITTI odometry
- Georgia Tech Smoothing and Mapping (GTSAM)
- CasADi + do-mpc
- evo for trajectory error

**Default stack:** Ubuntu 22.04, or Windows Subsystem for Linux 2 (WSL2) with Ubuntu 22.04. ROS 2 Humble’s documented install is Debian packages on Ubuntu. Do not make macOS + Docker the required path.

---

## Anti-patterns (all milestones)

- Do **not** buy a drone, lidar, Jetson, motion-capture hall, or wind tunnel. That was why this subject beat aero shop work: it is reachable in simulation.
- Do **not** add mechanical/aerospace scope: finite-element analysis, airfoils, engine maps, coupon tests, computer-aided design as a second Deep.
- Do **not** skip the predict/update derivation and only call `filterpy`. Library-calling is the check *after* your code matches.
- Do **not** collect 40 ROS packages. Humble CLI + one publisher + `tf2` is the ROS 2 bar until M9.
- Do **not** start with ORB-SLAM3 as the first VIO. It is heavier to build; OpenVINS is the VIO/IMU spine. ORB-SLAM3 is optional after M6 if the machine can compile it.
- Do **not** start with Gazebo Harmonic if jMAVSim flies. Gazebo is allowed only if jMAVSim is blocked and you still need a 3-D plant.
- Do **not** call SITL “flight test.”
- Do **not** inflate into Palantir fusion, entity resolution, DISARM, or general networking (routing/switching). Onboard estimation is not Gotham.
- Do **not** inflate into controller-area network (CAN), time-sensitive networking (TSN), or Link-16. Those are later hires.
- Do **not** run H∞ as the core. Robust control is a branch. The spine is KF + MPC.
- Do **not** train a huge vision model to “do SLAM.” Run a published VIO on a public log.

---

## Milestone sequence

**Total:** about **160 hours** (≈ **6 Thursday–Saturday blocks** at 30 h/week). Install overruns are real; 7–8 weeks is still a finish, 16 weeks of “reading robotics Twitter” is not.

### M1 — State, Gaussian, covariance (10 h)

**Do**

1. Read Kalmanfilter.net 1-D Kalman (HTTP 200): https://kalmanfilter.net/kalman1d.html  
2. Keep NumPy/SciPy/Matplotlib docs in reach (HTTP 200): https://numpy.org/doc/stable/ · https://docs.scipy.org/doc/scipy/ · https://matplotlib.org/stable/  
3. Write, from scratch, a 1-D constant-velocity simulator: true `x`, noisy `z`, plot both. No filter yet.
4. Write the mean and covariance of a 2-D Gaussian; draw 100 samples; confirm the sample covariance is close.

**Spoken-recall checkpoint**  
“What is a state, what is a measurement, and why is covariance a matrix instead of one number?”

**Exit this milestone when** you can say that without looking, and the 1-D plot exists in a repo folder.

---

### M2 — Linear Kalman filter from scratch (14 h)

**Do**

1. Finish the 1-D filter on Kalmanfilter.net (same URL as M1).  
2. Work Rlabbe, *Kalman and Bayesian Filters in Python*, preface + Kalman chapters **as a check, not a copy-paste** (HTTP 200): https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python  
3. FilterPy KF reference **after** yours runs (HTTP 200): https://filterpy.readthedocs.io/en/latest/kalman/KalmanFilter.html · https://github.com/rlabbe/filterpy  
4. Implement predict (`x`, `P` through `F`, `Q`) and update (`K`, `x`, `P` through `H`, `R`) in NumPy for 1-D then 2-D constant-velocity. No FilterPy inside the function.
5. Overlay your `x` on FilterPy’s on the same noise sequence. They should match to numerical noise.

**Spoken-recall checkpoint**  
“Write the predict equations, then the update equations, in words: what does `K` do to `P`?”

---

### M3 — EKF and UKF from scratch (16 h)

**Do**

1. Extended Kalman: https://kalmanfilter.net/ekf.html (HTTP 200)  
2. Unscented Kalman: https://kalmanfilter.net/ukf.html (HTTP 200)  
3. FilterPy EKF / UKF pages (HTTP 200): https://filterpy.readthedocs.io/en/latest/kalman/ExtendedKalmanFilter.html · https://filterpy.readthedocs.io/en/latest/kalman/UnscentedKalmanFilter.html  
4. Attitude / error-state literacy (read, do not re-derive the whole report): Solà, “Quaternion kinematics for the error-state Kalman filter,” arXiv **1502.01030** (HTTP 200): https://arxiv.org/abs/1502.01030 · PDF https://arxiv.org/pdf/1502.01030  
5. Implement a **nonlinear** plant (e.g. 2-D unicycle, or range-bearing to a beacon). Jacobian EKF *and* UKF sigma-point version. Compare on the same seed to FilterPy.
6. Deliberately break the linearization (large angle step). See EKF diverge while UKF degrades slower — or document if both die. Honesty > a pretty plot.

**Spoken-recall checkpoint**  
“When is the EKF’s Jacobian a lie, and what does the UKF do instead of that Jacobian?”

---

### M4 — Noise, observability, consistency (10 h)

**Do**

1. Sweep `Q` and `R` on the M2 filter. Too-small `R`: overfit measurements. Too-small `Q`: trust a dead model.
2. Compute NIS on the innovation sequence; NEES on the error vs truth. Say whether the filter is consistent, optimistic, or pessimistic.
3. One spoken sentence tying Phase 1: **SDT decides a hypothesis; this filter estimates a vector.** Thresholds still exist (gating an innovation) — that is the cousin, not a new ROC course.
4. Optional public-domain attitude note (HTTP 200), only if M3 quaternions confused you: Markley, NASA NTRS **20040037784**, *Multiplicative Versus Additive Filtering for Spacecraft Attitude Determination*: https://ntrs.nasa.gov/citations/20040037784 · PDF https://ntrs.nasa.gov/api/citations/20040037784/downloads/20040037784.pdf  

**Spoken-recall checkpoint**  
“If NEES is always huge, is `P` too small or too big, and what would you touch first, `Q` or `R`?”

---

### M5 — ROS 2 Humble, topics, `tf2` (12 h)

**Do**

1. Install from the Humble Debian page (HTTP 200): https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html — hub: https://docs.ros.org/en/humble/Installation.html  
2. Beginner CLI tutorials (HTTP 200): https://docs.ros.org/en/humble/Tutorials.html · https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools.html  
3. Python publisher/subscriber (HTTP 200): https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html  
4. Topics / services / actions (HTTP 200): https://docs.ros.org/en/humble/How-To-Guides/Topics-Services-Actions.html  
5. `tf2` concept + static broadcaster (HTTP 200): https://docs.ros.org/en/humble/Concepts/Basic/About-TF2.html · https://docs.ros.org/en/humble/p/tf2/ · https://docs.ros.org/en/humble/Tutorials/Intermediate/Tf2/Writing-A-Tf2-Static-Broadcaster-Py.html · https://github.com/ros2/geometry2  
6. Publish a fake `PoseStamped` from your M2 filter at 50 hertz. `echo` it. Broadcast `map` → `base_link`. `tf2_echo` shows it.

**Spoken-recall checkpoint**  
“What is a topic versus a TF frame, and why does a filter that does not timestamp its pose poison the tree?”

---

### M6 — EuRoC + OpenVINS (18 h)

**Do**

1. Dataset paper (HTTP 200): Burri et al., “The EuRoC micro aerial vehicle datasets,” arXiv **1605.05732**: https://arxiv.org/abs/1605.05732 · PDF https://arxiv.org/pdf/1605.05732  
2. Files: ETH Research Collection DOI **10.3929/ethz-b-000690084** (HTTP 200, named redirect to handle `20.500.11850/690084`): https://doi.org/10.3929/ethz-b-000690084  
   Entity page (HTTP 200): https://www.research-collection.ethz.ch/entities/researchdata/bcaf173e-5dac-484b-bc37-faf97a594f1f  
   ASL index (HTTP 200, named redirect from `ethz-asl.github.io/datasets/`): https://ethz-asl.github.io/datasets/  
   Single sequence **MH_01_easy** zip (HTTP 200): https://www.research-collection.ethz.ch/bitstream/handle/20.500.11850/263889/1/MH_01_easy.zip  
   The old wiki https://projects.asl.ethz.ch/datasets/doku.php?id=kmavvisualinertialdatasets **200s but the body says the resource moved** — use the Research Collection, not the wiki as the file host.  
3. OpenVINS (HTTP 200): https://github.com/rpng/open_vins · docs https://docs.openvins.com/ · install https://docs.openvins.com/gs-installing.html · tutorial https://docs.openvins.com/gs-tutorial.html  
4. Run OpenVINS on **MH_01_easy**. Save estimated trajectory vs ground truth.  
5. Evaluate with evo (HTTP 200): https://github.com/MichaelGrupp/evo — report **absolute trajectory error (ATE)** and **relative pose error (RPE)**. If ATE is garbage, fix frames/time, do not “tune until the plot looks straight” without a number.  
6. Optional later, not this milestone: ORB-SLAM3 paper arXiv **2007.11898** (HTTP 200) https://arxiv.org/abs/2007.11898 · code https://github.com/UZ-SLAMLab/ORB_SLAM3 — only if OpenVINS already produced an ATE.

**Spoken-recall checkpoint**  
“What sensors are on EuRoC, what is ground truth, and what would a good ATE on MH_01 mean that a pretty video does not?”

---

### M7 — KITTI odometry (12 h)

**Do**

1. KITTI site + odometry eval (HTTP 200): https://www.cvlibs.net/datasets/kitti/ · https://www.cvlibs.net/datasets/kitti/eval_odometry.php · setup https://www.cvlibs.net/datasets/kitti/setup.php · kitti.org odometry (HTTP 200): https://www.kitti.org/ · https://www.kitti.org/data/odometry/  
2. Paper PDF (HTTP 200): Geiger, Lenz, Urtasun, CVPR 2012, https://www.cvlibs.net/publications/Geiger2012CVPR.pdf  
3. Download **one** odometry sequence with ground truth (sequence 00 or 07). Do not download the whole raw corpus.  
4. Run a **stereo or visual-odometry path you can explain** (OpenVINS if you have stereo IMU, or a minimal essential-matrix / 2-D–2-D pipeline you wrote). evo ATE vs KITTI poses.  
5. Optional bag bridge (HTTP 200): https://github.com/tomas789/kitti2bag — only if you are feeding ROS 2. Do not make bag conversion the milestone.

**Spoken-recall checkpoint**  
“KITTI is a car, EuRoC is a MAV. What breaks in your estimator when scale, IMU, and loop-closures change between those two?”

---

### M8 — Factor graphs / GTSAM (14 h)

**Do**

1. GTSAM (HTTP 200): https://gtsam.org/ · get started https://gtsam.org/get_started/ · intro tutorial https://gtsam.org/tutorials/intro.html · code https://github.com/borglab/gtsam · wiki https://github.com/borglab/gtsam/wiki  
2. iSAM2 paper (HTTP 200): Kaess et al., arXiv **1207.4759** https://arxiv.org/abs/1207.4759  
3. Build a **pose-graph** of 2-D poses with odometry edges + one loop-closure. Optimize. Show the loop pull the tail in.  
4. Add one IMU or GPS-like factor from the tutorials if the Python examples install. If the Python install fails, the 2-D pose-graph in C++ examples still counts — say which.

**Spoken-recall checkpoint**  
“What is a factor, what is a variable, and how is a batch pose-graph different from a causal Kalman filter?”

---

### M9 — PX4 SITL, jMAVSim (14 h)

**Do**

1. PX4 docs hub (HTTP 200): https://docs.px4.io/main/en/  
2. Ubuntu dev env (HTTP 200): https://docs.px4.io/main/en/dev_setup/dev_env_linux_ubuntu.html  
3. Simulation overview (HTTP 200): https://docs.px4.io/main/en/simulation/  
4. **jMAVSim** (HTTP 200): https://docs.px4.io/main/en/sim_jmavsim/  
5. Simulation-in-hardware (SIH) if Java/jMAVSim is blocked (HTTP 200): https://docs.px4.io/main/en/sim_sih/  
6. Autopilot tree (HTTP 200): https://github.com/PX4/PX4-Autopilot  
7. MAVLink (HTTP 200): https://mavlink.io/en/ · PX4 MAVLink middleware https://docs.px4.io/main/en/middleware/mavlink.html  
8. MAVSDK Python quickstart (HTTP 200): https://mavsdk.mavlink.io/main/en/index.html · https://mavsdk.mavlink.io/main/en/python/quickstart.html  
9. Build PX4 SITL; start jMAVSim; **arm, takeoff, hover, land** via MAVSDK or the documented commander. Record a screen video.  
10. Gazebo only if jMAVSim will not run (HTTP 200): https://docs.px4.io/main/en/sim_gazebo_gz/ — still SITL, still not hardware.

**Spoken-recall checkpoint**  
“What is SITL versus a real IMU, and which loops (estimation, rate, position) are you actually closing in jMAVSim?”

---

### M10 — MPC on a planar plant (16 h)

**Do**

1. Underactuated Robotics, trajectory optimization (HTTP 200): https://underactuated.csail.mit.edu/ · intro https://underactuated.csail.mit.edu/intro.html · trajopt https://underactuated.csail.mit.edu/trajopt.html · acrobot https://underactuated.csail.mit.edu/acrobot.html · Drake chapter https://underactuated.csail.mit.edu/drake.html  
   Mirror: https://underactuated.mit.edu/ · https://underactuated.mit.edu/trajopt.html  
2. CasADi (HTTP 200): https://web.casadi.org/ · get https://web.casadi.org/get/ · docs https://web.casadi.org/docs/ · Opti blog https://web.casadi.org/blog/opti/ · code https://github.com/casadi/casadi  
3. do-mpc (HTTP 200): https://www.do-mpc.com/en/latest/ · getting started https://www.do-mpc.com/en/latest/getting_started.html · oscillating-masses example https://www.do-mpc.com/en/latest/example_gallery/oscillating_masses_discrete.html · https://github.com/do-mpc/do-mpc  
4. Optional racing MPC paper (HTTP 200): Liniger, Domahidi, Morari, RSS 2011, https://www.roboticsproceedings.org/rss11/p40.pdf · HTML https://www.roboticsproceedings.org/rss11/p40.html — **read the formulation**, do not build a full race car.  
5. Implement discrete MPC on a **2-D double integrator or unicycle**: horizon `N`, input limits, hit a waypoint. Plot planned vs applied. If the solver fails at the constraint, say so.

**Spoken-recall checkpoint**  
“What is predicted over the horizon, what is applied to the plant, and what happens if the model in the MPC is not the model you simulate?”

---

### M11 — Close a loop in SITL (14 h)

**Do**

1. PX4 offboard (HTTP 200): https://docs.px4.io/main/en/flight_modes/offboard.html  
2. ROS 2 + PX4 (HTTP 200): https://docs.px4.io/main/en/ros2/user_guide.html · offboard control https://docs.px4.io/main/en/ros2/offboard_control.html · control interface https://docs.px4.io/main/en/ros2/px4_ros2_control_interface.html  
3. **Path A (required):** offboard **position setpoints** to fly a square in jMAVSim. PX4’s own controller stays in the loop. This is still a win.  
4. **Path B (the actual control spine):** replace the outer loop on a **simple** plant (the M10 unicycle, or PX4 only if you can still explain every block) with your MPC, using an EKF state. If PX4 offboard rejects your rates, **fall back to Path A plus M10 on the toy plant wired to the EKF** and say that PX4’s inner loop stayed closed. Do not fake a custom rate controller you did not stabilize.

**Spoken-recall checkpoint**  
“Name the blocks: sensors → estimator → planner/MPC → mixer. Which of those did *you* write, and which did PX4 keep?”

---

### M12 — Portfolio lock (12 h)

**Do**

1. Public repo: `README` with reproduce commands (Humble, PX4 tag, EuRoC sequence, Python pins).  
2. **Demo 1:** NumPy KF/EKF/UKF vs FilterPy on a seed, plus NEES plot.  
3. **Demo 2:** OpenVINS on EuRoC MH_01, evo ATE/RPE numbers in the README.  
4. **Demo 3:** jMAVSim takeoff/hover **or** offboard square; video. Caption: **SITL only**.  
5. **Demo 4:** CasADi/do-mpc waypoint on the planar plant.  
6. Findings write-up (one page in the README, not a journal): what broke, what is simulated-only, what you would not claim to a flight test engineer.  
7. Recorded walkthrough: you, no notes, walking M2 equations → M6 ATE → M10 horizon → M11 block diagram.

**Spoken-recall checkpoint (this is the Phase 3 gate)**  
The walkthrough *is* the checkpoint. If you cannot do it without the README, the lock is not closed.

---

## 10/10 means

All of these, not a vibe:

1. Predict and update for a linear KF, spoken, including what `K` does to `P`.  
2. EKF vs UKF in one minute, including a case where linearization is the failure.  
3. NEES/NIS: you can say whether a filter is lying about its uncertainty.  
4. OpenVINS (or a VIO you can defend) on **EuRoC MH_01** with a published ATE, not a screenshot of RViz.  
5. One KITTI sequence with a number, and a spoken difference vs EuRoC.  
6. A GTSAM (or equivalent) pose-graph that actually uses a loop-closure.  
7. PX4 SITL hover or offboard square **and** the sentence “this is not hardware.”  
8. MPC on a constrained planar plant you can derive.  
9. Block diagram of M11: your code vs PX4’s.  
10. Public repo a stranger can clone; video; README; spoken walkthrough without notes.

If any item is “I watched a PX4 video,” the score is not 10.

---

## What this does *not* claim

- Specialist depth **on a vehicle with a safety-of-flight process**. That needs a shop, a range, and a later mechanical/aerospace hire.  
- Director-tier radio-frequency / tactical links.  
- A Palantir-style fusion desk.  
- Production autopilot certification (DO-178C lives on the industry map as functional safety; it is not this curriculum).

**After 10/10:** keep the three home Deeps as Phase 1 / Phase 2 / Phase 3. Do not add a fourth. Hardware flight is a **company resource**, not the next PDF.

---

## URL log (checked 24 November 2026, America/New_York)

| URL | Result |
|-----|--------|
| https://kalmanfilter.net/kalman1d.html | 200 |
| https://kalmanfilter.net/ekf.html | 200 |
| https://kalmanfilter.net/ukf.html | 200 |
| https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python | 200 |
| https://github.com/rlabbe/filterpy | 200 |
| https://filterpy.readthedocs.io/en/latest/kalman/KalmanFilter.html | 200 |
| https://filterpy.readthedocs.io/en/latest/kalman/ExtendedKalmanFilter.html | 200 |
| https://filterpy.readthedocs.io/en/latest/kalman/UnscentedKalmanFilter.html | 200 |
| https://numpy.org/doc/stable/ | 200 |
| https://docs.scipy.org/doc/scipy/ | 200 |
| https://matplotlib.org/stable/ | 200 |
| https://arxiv.org/abs/1502.01030 | 200 |
| https://ntrs.nasa.gov/citations/20040037784 | 200 |
| https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html | 200 |
| https://docs.ros.org/en/humble/Tutorials.html | 200 |
| https://docs.ros.org/en/humble/Concepts/Basic/About-TF2.html | 200 |
| https://docs.px4.io/main/en/simulation/ | 200 |
| https://docs.px4.io/main/en/sim_jmavsim/ | 200 |
| https://docs.px4.io/main/en/sim_sih/ | 200 |
| https://docs.px4.io/main/en/sim_gazebo_gz/ | 200 |
| https://docs.px4.io/main/en/ros2/user_guide.html | 200 (named path `/ros2/user_guide`) |
| https://github.com/PX4/PX4-Autopilot | 200 |
| https://mavsdk.mavlink.io/main/en/python/quickstart.html | 200 |
| https://doi.org/10.3929/ethz-b-000690084 | 200 → `.../handle/20.500.11850/690084` |
| https://www.research-collection.ethz.ch/bitstream/handle/20.500.11850/263889/1/MH_01_easy.zip | 200 |
| https://ethz-asl.github.io/datasets/ | 200 → ASL datasets index |
| https://arxiv.org/abs/1605.05732 | 200 |
| https://github.com/rpng/open_vins | 200 |
| https://docs.openvins.com/gs-installing.html | 200 |
| https://github.com/MichaelGrupp/evo | 200 |
| https://www.cvlibs.net/datasets/kitti/ | 200 |
| https://www.cvlibs.net/datasets/kitti/eval_odometry.php | 200 |
| https://www.cvlibs.net/publications/Geiger2012CVPR.pdf | 200 |
| https://gtsam.org/ | 200 |
| https://arxiv.org/abs/1207.4759 | 200 |
| https://web.casadi.org/ | 200 |
| https://www.do-mpc.com/en/latest/getting_started.html | 200 |
| https://underactuated.csail.mit.edu/trajopt.html | 200 |
| https://www.roboticsproceedings.org/rss11/p40.pdf | 200 |
| https://github.com/UZ-SLAMLab/ORB_SLAM3 | 200 (optional) |
| https://arxiv.org/abs/2007.11898 | 200 (optional) |

**Dropped (not used):** UNC Welch `kalman_intro.pdf` (404); `probabilistic-robotics.org` (failed); MIT Press book page (403); old EuRoC wiki as file host (200 but **moved**); `docs.px4.io/.../jmavsim.html` (404 — live path is `/sim_jmavsim/`); classic Gazebo sim URL (404 — live path is `/sim_gazebo_gz/`).
