# PERCEPTION / CONTROL MAP — PLAIN ENGLISH

Mechanics map (physical-instrument). Not a Branches map and not a Mind map. Companion to **Strategic Doctrine** and **Autonomous Weapons / Counter-UAS** — those say *whether* a system may act and *what* the weapon is. This map is the math/code spine that answers *where the vehicle is* and *what command is legal for the plant*. It is **not** the Phase 3 checkpoint curriculum (`docs/study/PHASE3_PERCEPTION_CONTROL.md` / `docs/study/HOME_LEARNABLE_CURRICULUM.md`). That file is the Do-list. This file is the subject.

Confirmed Deep physical subject **23 Nov 2026**. Replaces the earlier mechanical/aerospace-shop choice because this stack is reachable on a laptop (simulation + public logs). A hover in software-in-the-loop is **not** a hardware-validated flight. Say that every time.

Pull date **24 Nov 2026**, America/New_York.

Do not mash machines. A Kalman filter is not SLAM. SLAM is not “the camera model.” MPC is not PID with extra steps. EKF is not UKF. Estimation is not detection (that is signal detection theory in Phase 1). SITL is not a range test. Doctrine is not a covariance.

---

## What this is

An autonomous stack that moves in the world has two jobs that never go away:

1. **Perception / estimation** — given a messy stream of sensors, a belief about state (position, velocity, attitude, maybe a map) plus an honest uncertainty.
2. **Control** — given that belief, a command the plant can actually execute under constraints (thrust limits, no-fly, actuator rate).

The spine is **Kalman filtering** (linear / **EKF** extended / **UKF** unscented), **SLAM** / visual-inertial odometry as *estimation*, **MPC** as constrained receding-horizon control, and **consistency checks** (does the filter’s claimed uncertainty match its errors?).

If you cannot say those four in one breath, you do not have the subject. You have a ROS screenshot.

---

## What this is not

- **Not** mechanical/aerospace shop work (airfoils, coupons, FEA, engine maps, CAD as a Deep). That hire still exists later. It is not this Deep.
- **Not** Palantir-style fusion / link analysis. Onboard `x̂` is not a Gotham graph.
- **Not** radio / Link-16 / TSN / CAN as Director fluency. Those are later hires.
- **Not** production autopilot certification (**DO-178C**). That sits on Industry Structure / Standards as a door, not as this math.
- **Not** “train a huge vision model to do SLAM.” Published VIO on a public log is the subject.
- **Not** H∞ as the core. Robust control is a branch. The spine is KF + MPC.
- **Not** Strategic Doctrine (when force is authorized) and **not** Autonomous Weapons (what the effector is, C-UAS patterns). Those notes stay. This note does not replace them.

---

## How it actually works

**Predict.** A motion model says: if the vehicle was here, and we commanded that, it should be there, with process noise `Q` because the model is wrong on purpose.

**Update.** A measurement arrives, with its own noise `R`. The Kalman gain `K` is the compromise: trust the model vs trust the sensor. After the update, covariance `P` should shrink if the measurement was informative.

**Linear KF.** Model and measurement are linear. Closed form. If your plant is actually linear and your `Q`/`R` are honest, this is the whole trick.

**EKF.** Linearize about the current estimate. Cheap. Dies when the operating point is far from where you linearized (big attitude error, bad init, strong nonlinearity in the measurement).

**UKF.** Push a small set of sigma points through the real nonlinear functions, rebuild mean/covariance. Costlier. Helps when linearization is the failure. Not magic: garbage `Q`/`R` still lies.

**SLAM / VIO.** You do not only estimate “where am I in a known map.” You estimate pose **and** the map (or a sliding window of poses + IMU biases + landmarks). Visual-inertial odometry is camera + IMU as the workhorse. Loop closures (GTSAM-style pose graphs) are how drift gets killed when you recognize a place again.

**MPC.** At each step, solve a short-horizon optimization: stay near the plan, obey constraints, apply the first command, repeat. PID is a local stitch. MPC is the thing that can refuse an infeasible waypoint instead of saturating blindly.

**Consistency.** **NEES** / **NIS** ask whether errors are the size `P` promised. A filter that is “accurate” but overconfident is a liar. Autonomy stacks die from liars more often than from noisy-but-honest filters.

---

## How it actually fails

- **Wrong `Q`/`R`.** Too-small `R` → you believe a spoofed or biased sensor. Too-small `Q` → you believe a dead model. The math still runs. The vehicle is lost.
- **Unmodeled dynamics.** Ground effect, sloshing, delayed thrust, a gimbal you pretended was rigid. The residual is not Gaussian-white. EKF/UKF will still print a number.
- **Time.** A measurement with the wrong timestamp is a different planet. Fusion without a clock discipline is theater.
- **Init.** EKF with a bad initial attitude is a famous way to watch `P` get small around the wrong `x̂`.
- **No loop closure.** VIO without a loop is a fancy odometer. Long missions drift. Calling that “a map” is the mash.
- **Constraint-blind control.** High-gain tracking that ignores actuator limits looks fine until the first saturation, then the estimator and the controller fight.
- **SITL pride.** A jMAVSim hover proves the interfaces. It does not prove IMU scale factor, camera calibration, vibration, or GPS-denied reality. The curriculum forbids calling it flight test. This map forbids it too.
- **Sensor attack.** GPS spoof, captured camera, IMU bias injection. If the filter has no residual gate, it will track the lie with high confidence. That is an **estimation** failure that doctrine and C-UAS notes care about. Do not hide it under “AI.”
- **SDT mash.** Detection (is this H1?) is Phase 1. Estimation (where is `x`?) is this map. Same probability objects, different question. Restudying ROC curves under a robotics sticker is a stall.

---

## Companion, not duplicate

| Note | Job |
|------|-----|
| **Strategic Doctrine Map** | Who may authorize an act; what “use of force” even is. |
| **Autonomous Weapons / Counter-UAS** | Effectors, C-UAS patterns, policy mouths. |
| **Engineering Map** | How engineering *as a field* is hired and gated. |
| **AI / Technical Map** | CS/AI landscape. Prompt injection and models live there. Filters do not. |
| **AI Security → ML-KEM → Perception curriculum** | The checkpoint Do-list. Hours, URLs, 10/10 artifacts. |
| **This map** | What the physical Deep *is*, how the machines differ, how they fail. |

Read this before or beside Phase 3. Do not paste Phase 3 milestones into Apple Notes as if they were this map.

---

## Company use (later physical-autonomy shop)

The long-term company vision needs a stack that can **fail closed** when `P` is dishonest or the MPC problem is infeasible — same moral as Gate’s act-receipt: if you cannot open an honest state, you do not have a GO. That sentence is why this Deep exists.

It does **not** buy the 2026 software-security hire. Phase 1 then Phase 2 still go first. This Deep starts after Phase 2’s *home* 10/10. Parallelizing two Deeps on Thu–Sat is how both stay unfinished.

Hardware flight is a **company resource** (range, safety-of-flight, later aero hire). It is not the next PDF and not a fourth Deep.

---

## OPEN

- Which commercial autopilot’s published covariance is actually consistent on a named public log — not copied here; the curriculum uses EuRoC / KITTI / SITL, not a vendor brochure.
- DO-178C / STANAG 4703 as a *cert path* for a future vehicle — Industry / Standards notes, not this map.
- Exact C-UAS sensor-fusion architecture of any named military program — classified or brochure; **OPEN**, not guessed.

---

## Falsifier

If Phase 3 is quietly swapped back to aero shop work as the Deep, this map is retired. If “perception/control” is used to mean Palantir fusion or prompt injection, cell “What this is” dies. If SITL hover is treated as hardware-validated flight in a public claim, the honesty clause dies.
